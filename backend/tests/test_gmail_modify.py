import io
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from app.services.gmail_access import GmailAccessError
from app.services.gmail_inbox import GmailClient
from app.services.gmail_modify import create_label, delete_label, modify_message
from app.services.google_oauth import OAuthTokens


class GmailModifyTests(unittest.TestCase):
    def test_all_actions_change_only_requested_label_and_read_back_same_message(self) -> None:
        for action, label_id, expected_label, adding in (
            ("star", None, "STARRED", True),
            ("unstar", None, "STARRED", False),
            ("add-label", "Label_1", "Label_1", True),
            ("remove-label", "Label_1", "Label_1", False),
            ("add-label", "IMPORTANT", "IMPORTANT", True),
            ("remove-label", "IMPORTANT", "IMPORTANT", False),
        ):
            with self.subTest(action=action), patch("app.services.gmail_modify.GmailClient") as client_class:
                client = client_class.return_value
                before = ["INBOX"] if adding else ["INBOX", expected_label]
                after = ["INBOX", expected_label] if adding else ["INBOX"]
                client.get_json.side_effect = (
                    [{"labels": [
                        {"id": "Label_1", "type": "user"},
                        {"id": "IMPORTANT", "type": "system"},
                    ]}] if label_id else []
                ) + [{"id": "abc", "labelIds": before}, {"id": "abc", "labelIds": after}]
                client.post_json.return_value = {"id": "abc"}

                modify_message("abc", action, label_id)

                self.assertEqual(client.post_json.call_count, 1)
                url, body = client.post_json.call_args.args
                self.assertEqual(url, "https://gmail.googleapis.com/gmail/v1/users/me/messages/abc/modify")
                self.assertEqual(body, {
                    "addLabelIds": [expected_label] if adding else [],
                    "removeLabelIds": [] if adding else [expected_label],
                })
                self.assertEqual(client.get_json.call_args.args[0],
                                 "https://gmail.googleapis.com/gmail/v1/users/me/messages/abc?format=minimal")

    def test_rejects_invalid_target_and_system_label_before_modifying(self) -> None:
        with patch("app.services.gmail_modify.GmailClient") as client_class:
            with self.assertRaisesRegex(GmailAccessError, "Invalid message ID"):
                modify_message("abc/def", "star")
            client_class.assert_not_called()

            client_class.return_value.get_json.return_value = {
                "labels": [
                    {"id": "UNREAD", "type": "system"},
                    {"id": "CATEGORY_PERSONAL", "type": "system"},
                    {"id": "CATEGORY_SOCIAL", "type": "system"},
                ]
            }
            with self.assertRaisesRegex(GmailAccessError, "cannot be edited"):
                modify_message("abc", "add-label", "UNREAD")
            with self.assertRaisesRegex(GmailAccessError, "cannot be edited"):
                modify_message("abc", "add-label", "CATEGORY_PERSONAL")
            with self.assertRaisesRegex(GmailAccessError, "cannot be edited"):
                modify_message("abc", "add-label", "CATEGORY_SOCIAL")
            with self.assertRaisesRegex(GmailAccessError, "cannot be edited"):
                modify_message("abc", "add-label", "PURCHASES")
            client_class.return_value.post_json.assert_not_called()

    def test_create_label_checks_account_and_confirms_new_gmail_label(self) -> None:
        with patch("app.services.gmail_modify.GmailClient") as client_class:
            client = client_class.return_value
            client.profile_address.return_value = "me@example.com"
            client.get_json.side_effect = [
                {"labels": []},
                {"labels": [{"id": "Label_123", "name": "Work", "type": "user"}]},
            ]
            client.post_json.return_value = {"id": "Label_123"}
            result = create_label(" Work ", "me@example.com")
            self.assertEqual(result, {"id": "Label_123", "name": "Work", "kind": "user", "modifiable": True, "deletable": True})
            client.post_json.assert_called_once_with(
                "https://gmail.googleapis.com/gmail/v1/users/me/labels",
                {"name": "Work", "labelListVisibility": "labelShow", "messageListVisibility": "show"},
            )

    def test_create_label_rejects_duplicate_or_wrong_account_before_post(self) -> None:
        with patch("app.services.gmail_modify.GmailClient") as client_class:
            client = client_class.return_value
            client.profile_address.return_value = "other@example.com"
            with self.assertRaisesRegex(GmailAccessError, "account changed"):
                create_label("Work", "me@example.com")
            client.profile_address.return_value = "me@example.com"
            client.get_json.return_value = {"labels": [{"id": "Label_1", "name": "work", "type": "user"}]}
            with self.assertRaisesRegex(GmailAccessError, "already exists"):
                create_label("Work", "me@example.com")
            with self.assertRaisesRegex(GmailAccessError, "Invalid label name"):
                create_label("  ", "me@example.com")
            client.post_json.assert_not_called()

    def test_delete_label_only_allows_user_label_and_checks_gmail_afterward(self) -> None:
        with patch("app.services.gmail_modify.GmailClient") as client_class:
            client = client_class.return_value
            client.profile_address.return_value = "me@example.com"
            client.get_json.side_effect = [
                {"labels": [{"id": "Label_123", "name": "Work", "type": "user"}]},
                {"labels": []},
            ]
            delete_label("Label_123", "me@example.com")
            client.delete_json.assert_called_once_with(
                "https://gmail.googleapis.com/gmail/v1/users/me/labels/Label_123"
            )

            client.get_json.side_effect = None
            client.get_json.return_value = {"labels": [{"id": "IMPORTANT", "type": "system"}]}
            with self.assertRaisesRegex(GmailAccessError, "Only Gmail user labels"):
                delete_label("IMPORTANT", "me@example.com")
            client.delete_json.assert_called_once()

    def test_delete_request_uses_backend_token_and_handles_empty_response(self) -> None:
        with patch("app.services.gmail_inbox.load_local_tokens", return_value=OAuthTokens("private-token", None)):
            with patch("app.services.gmail_inbox.urlopen", return_value=io.BytesIO(b"")) as send:
                result = GmailClient().delete_json("https://gmail.googleapis.com/gmail/v1/users/me/labels/Label_123")
        self.assertEqual(result, {})
        request = send.call_args.args[0]
        self.assertEqual(request.get_method(), "DELETE")
        self.assertEqual(request.get_header("Authorization"), "Bearer private-token")

    def test_requires_same_message_and_confirmed_state(self) -> None:
        with patch("app.services.gmail_modify.GmailClient") as client_class:
            client = client_class.return_value
            client.get_json.return_value = {"id": "other", "labelIds": []}
            with self.assertRaisesRegex(GmailAccessError, "different message"):
                modify_message("abc", "star")
            client.post_json.assert_not_called()

            client.get_json.side_effect = [
                {"id": "abc", "labelIds": []},
                {"id": "abc", "labelIds": []},
            ]
            client.post_json.return_value = {"id": "abc"}
            with self.assertRaisesRegex(GmailAccessError, "did not confirm"):
                modify_message("abc", "star")

    def test_connected_page_rejects_changed_account_and_non_inbox_message(self) -> None:
        with patch("app.services.gmail_modify.GmailClient") as client_class:
            client = client_class.return_value
            client.profile_address.return_value = "other@example.com"
            with self.assertRaisesRegex(GmailAccessError, "account changed"):
                modify_message("abc", "star", expected_account="me@example.com", inbox_only=True)
            client.post_json.assert_not_called()

            client.profile_address.return_value = "me@example.com"
            client.get_json.return_value = {"id": "abc", "labelIds": ["SENT"]}
            with self.assertRaisesRegex(GmailAccessError, "not in the inbox"):
                modify_message("abc", "star", expected_account="me@example.com", inbox_only=True)
            client.post_json.assert_not_called()

    def test_post_uses_backend_token_and_safe_error(self) -> None:
        with patch("app.services.gmail_inbox.load_local_tokens", return_value=OAuthTokens("private-token", None)):
            with patch("app.services.gmail_inbox.urlopen", return_value=io.BytesIO(b'{"id":"abc"}')) as send:
                result = GmailClient().post_json("https://gmail.googleapis.com/gmail/v1/users/me/messages/abc/modify",
                                                 {"addLabelIds": ["STARRED"], "removeLabelIds": []})
            self.assertEqual(result["id"], "abc")
            request = send.call_args.args[0]
            self.assertEqual(request.get_method(), "POST")
            self.assertEqual(request.get_header("Authorization"), "Bearer private-token")
            self.assertIn(b'"addLabelIds": ["STARRED"]', request.data)

            denied = HTTPError("https://gmail.googleapis.com", 403, "private details", {}, None)
            with patch("app.services.gmail_inbox.urlopen", side_effect=denied):
                with self.assertRaises(GmailAccessError) as raised:
                    GmailClient().post_json("https://gmail.googleapis.com/gmail/v1/users/me/messages/abc/modify", {})
            self.assertNotIn("private-token", str(raised.exception))
            self.assertNotIn("private details", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
