import base64
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse

from app.services.gmail_access import GmailAccessError
from app.services.gmail_inbox import GmailClient, body_text, mailbox, read_message, sender_name
from app.services.google_oauth import OAuthTokens


class GmailInboxTests(unittest.TestCase):
    def test_mailbox_returns_real_account_and_newest_inbox_summaries(self) -> None:
        listing = {"messages": [{"id": "abc"}, {"id": "def"}]}
        first = {
            "id": "abc", "internalDate": "1000", "snippet": "first preview", "labelIds": ["INBOX"],
            "payload": {"headers": [{"name": "From", "value": "Alice <alice@example.com>"}, {"name": "Subject", "value": "First"}]},
        }
        second = {
            "id": "def", "internalDate": "2000", "snippet": "second preview", "labelIds": ["INBOX", "STARRED"],
            "payload": {"headers": [{"name": "From", "value": "Bob"}, {"name": "Subject", "value": "Second"}]},
        }
        with patch("app.services.gmail_inbox.GmailClient") as client_class:
            client = client_class.return_value
            client.profile_address.return_value = "me@example.com"
            client.get_json.side_effect = lambda url: (
                {"labels": [
                    {"id": "Label_1", "name": "Work", "type": "user"},
                    {"id": "CATEGORY_UPDATES", "name": "CATEGORY_UPDATES", "type": "system"},
                    {"id": "IMPORTANT", "name": "IMPORTANT", "type": "system"},
                    {"id": "INBOX", "name": "Inbox", "type": "system"},
                ]}
                if url.endswith("/labels") else listing if "?labelIds=" in url else first if "/abc?" in url else second
            )
            result = mailbox()
        self.assertEqual(result["account"], "me@example.com")
        self.assertEqual(result["labels"], [
            {"id": "IMPORTANT", "name": "Important", "kind": "system", "modifiable": True, "deletable": False},
            {"id": "Label_1", "name": "Work", "kind": "user", "modifiable": True, "deletable": True},
        ])
        self.assertEqual([item["id"] for item in result["messages"]], ["def", "abc"])
        self.assertEqual(result["messages"][0]["account"], "me@example.com")
        self.assertEqual(result["messages"][0]["sender"], "Bob")
        self.assertTrue(result["messages"][0]["starred"])
        self.assertIn("labelIds=INBOX", client.get_json.call_args_list[1].args[0])

    def test_read_message_returns_plain_text_for_search_hit_outside_inbox(self) -> None:
        encoded = base64.urlsafe_b64encode(b"Hello from Gmail").decode("ascii")
        data = {
            "id": "abc", "internalDate": "1000", "labelIds": ["INBOX"], "snippet": "Hello",
            "payload": {"mimeType": "text/plain", "body": {"data": encoded}, "headers": [{"name": "Subject", "value": "A message"}]},
        }
        with patch("app.services.gmail_inbox.GmailClient") as client_class:
            client_class.return_value.profile_address.return_value = "me@example.com"
            client_class.return_value.get_json.return_value = data
            result = read_message("abc")
            self.assertEqual(result["body"], "Hello from Gmail")
            data["labelIds"] = ["SENT"]
            self.assertEqual(read_message("abc")["body"], "Hello from Gmail")
        self.assertEqual(body_text({"mimeType": "text/html", "body": {"data": base64.urlsafe_b64encode(b"<p>Hi<script>bad()</script> there</p>").decode("ascii")}}), "Hi there")

    def test_mailbox_filters_inbox_by_gmail_label(self) -> None:
        with patch("app.services.gmail_inbox.GmailClient") as client_class:
            client = client_class.return_value
            client.profile_address.return_value = "me@example.com"
            client.get_json.side_effect = lambda url: (
                {"labels": [{"id": "Label_1", "name": "Work", "type": "user"}]}
                if url.endswith("/labels") else {"messages": []}
            )
            self.assertEqual(mailbox("STARRED")["messages"], [])
            self.assertIn("labelIds=INBOX&maxResults=50&labelIds=STARRED", client.get_json.call_args.args[0])
            self.assertEqual(mailbox("Label_1")["messages"], [])
            self.assertIn("labelIds=Label_1", client.get_json.call_args.args[0])
            with self.assertRaisesRegex(GmailAccessError, "Invalid mailbox label"):
                mailbox("PURCHASES")
            with self.assertRaisesRegex(GmailAccessError, "Invalid mailbox label"):
                mailbox("CATEGORY_PERSONAL")
            with self.assertRaisesRegex(GmailAccessError, "Invalid mailbox label"):
                mailbox("UNREAD")

    def test_search_passes_gmail_syntax_without_inbox_filter(self) -> None:
        with patch("app.services.gmail_inbox.GmailClient") as client_class:
            client = client_class.return_value
            client.profile_address.return_value = "me@example.com"
            client.get_json.side_effect = lambda url: (
                {"labels": []} if url.endswith("/labels") else {"messages": []}
            )
            result = mailbox(search_query='from:alice@example.com subject:"Quarterly Report"')
        self.assertEqual(result["messages"], [])
        url = client.get_json.call_args.args[0]
        self.assertIn("q=from%3Aalice%40example.com+subject%3A%22Quarterly+Report%22", url)
        self.assertNotIn("labelIds=INBOX", url)
        with self.assertRaisesRegex(GmailAccessError, "Invalid mailbox search"):
            mailbox(search_query=" ")
        with self.assertRaisesRegex(GmailAccessError, "Invalid mailbox search"):
            mailbox("STARRED", "hello")

    def test_mailbox_forwards_page_token_and_returns_next_token(self) -> None:
        with patch("app.services.gmail_inbox.GmailClient") as client_class:
            client = client_class.return_value
            client.profile_address.return_value = "me@example.com"
            client.get_json.side_effect = lambda url: (
                {"labels": []} if url.endswith("/labels") else
                {"messages": [], "nextPageToken": "later_token"}
            )
            result = mailbox(search_query="from:alice", page_token="earlier/token=")
        self.assertEqual(result["next_page_token"], "later_token")
        query = parse_qs(urlparse(client.get_json.call_args.args[0]).query)
        self.assertEqual(query, {"maxResults": ["50"], "pageToken": ["earlier/token="], "q": ["from:alice"]})

    def test_mailbox_rejects_invalid_page_data(self) -> None:
        with self.assertRaisesRegex(GmailAccessError, "Invalid page token"):
            mailbox(page_token=" ")
        with patch("app.services.gmail_inbox.GmailClient") as client_class:
            client = client_class.return_value
            client.profile_address.return_value = "me@example.com"
            client.get_json.side_effect = lambda url: (
                {"labels": []} if url.endswith("/labels") else
                {"messages": [], "nextPageToken": 123}
            )
            with self.assertRaisesRegex(GmailAccessError, "invalid page token"):
                mailbox()
            client.get_json.side_effect = lambda url: (
                {"labels": []} if url.endswith("/labels") else
                {"messages": [{"id": str(index)} for index in range(51)]}
            )
            with self.assertRaisesRegex(GmailAccessError, "invalid inbox"):
                mailbox()

    def test_sender_uses_display_name_without_quotes_or_address(self) -> None:
        self.assertEqual(
            sender_name({"headers": [{"name": "From", "value": '"黃哲宇" <cyhuang.cs15@nycu.edu.tw>'}]}),
            "黃哲宇",
        )
        self.assertEqual(
            sender_name({"headers": [{"name": "From", "value": "Google <no-reply@accounts.google.com>"}]}),
            "Google",
        )
        self.assertEqual(
            sender_name({"headers": [{"name": "From", "value": "someone@example.com"}]}),
            "someone",
        )

    def test_gmail_error_does_not_expose_token(self) -> None:
        denied = HTTPError("https://gmail.googleapis.com", 403, "private details", {}, None)
        with patch("app.services.gmail_inbox.load_local_tokens", return_value=OAuthTokens("private-token", None)):
            with patch("app.services.gmail_inbox.urlopen", side_effect=denied):
                with self.assertRaises(GmailAccessError) as raised:
                    GmailClient().get_json("https://gmail.googleapis.com/gmail/v1/users/me/messages")
        self.assertNotIn("private-token", str(raised.exception))
        self.assertNotIn("private details", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
