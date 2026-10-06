import base64
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

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
                    {"id": "INBOX", "name": "Inbox", "type": "system"},
                ]}
                if url.endswith("/labels") else listing if "?labelIds=" in url else first if "/abc?" in url else second
            )
            result = mailbox()
        self.assertEqual(result["account"], "me@example.com")
        self.assertEqual(result["labels"], [{"id": "CATEGORY_UPDATES", "name": "Updates"}, {"id": "Label_1", "name": "Work"}])
        self.assertEqual([item["id"] for item in result["messages"]], ["def", "abc"])
        self.assertEqual(result["messages"][0]["account"], "me@example.com")
        self.assertEqual(result["messages"][0]["sender"], "Bob")
        self.assertTrue(result["messages"][0]["starred"])
        self.assertIn("labelIds=INBOX", client.get_json.call_args_list[1].args[0])

    def test_read_message_returns_plain_text_and_rejects_non_inbox(self) -> None:
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
            with self.assertRaisesRegex(GmailAccessError, "not in the inbox"):
                read_message("abc")
        self.assertEqual(body_text({"mimeType": "text/html", "body": {"data": base64.urlsafe_b64encode(b"<p>Hi<script>bad()</script> there</p>").decode("ascii")}}), "Hi there")

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
