import unittest
from unittest.mock import Mock, patch

from app.services.gmail_access import GmailAccessError
from app.services.gmail_inbox import GmailNotFoundError
from app.services.mail_sync import history_changes, sync_mailbox


class MailSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = Mock()
        self.client.profile_address.return_value = "me@example.com"
        self.client.get_json.return_value = {"historyId": "42"}
        self.result = {"account": "me@example.com", "labels": [], "messages": [], "next_page_token": None}
        self.tokens = patch("app.services.mail_sync.load_local_tokens")
        self.client_patch = patch("app.services.mail_sync.GmailClient", return_value=self.client)
        self.tokens.start()
        self.client_patch.start()

    def tearDown(self) -> None:
        self.client_patch.stop()
        self.tokens.stop()

    def test_first_sync_builds_page_and_saves_cursor(self) -> None:
        with patch("app.services.mail_sync.sync_state", return_value=("me@example.com", None, [])):
            with patch("app.services.mail_sync.gmail_mailbox", return_value=self.result) as mailbox:
                with patch("app.services.mail_sync.store_synced_mailbox") as save:
                    sync_mailbox()
        mailbox.assert_called_once_with(None, None, None)
        save.assert_called_once_with(None, None, None, self.result, "42")

    def test_history_change_refreshes_cached_page(self) -> None:
        self.client.get_json.return_value = {"historyId": "43", "history": [{"id": "43"}]}
        with patch("app.services.mail_sync.sync_state", return_value=("me@example.com", "42", [(None, None, None)])):
            with patch("app.services.mail_sync.gmail_mailbox", return_value=self.result) as mailbox:
                with patch("app.services.mail_sync.store_synced_mailbox") as save:
                    sync_mailbox()
        mailbox.assert_called_once()
        save.assert_called_once_with(None, None, None, self.result, "43")

    def test_unchanged_history_advances_cursor_without_page_fetch(self) -> None:
        with patch("app.services.mail_sync.sync_state", return_value=("me@example.com", "42", [(None, None, None)])):
            with patch("app.services.mail_sync.gmail_mailbox") as mailbox:
                with patch("app.services.mail_sync.store_sync_cursor") as save:
                    sync_mailbox()
        mailbox.assert_not_called()
        save.assert_called_once_with("me@example.com", "42")

    def test_expired_history_falls_back_to_full_sync(self) -> None:
        self.client.get_json.side_effect = [GmailNotFoundError(), {"historyId": "50"}]
        with patch("app.services.mail_sync.sync_state", return_value=("me@example.com", "42", [(None, None, None)])):
            with patch("app.services.mail_sync.gmail_mailbox", return_value=self.result):
                with patch("app.services.mail_sync.store_synced_mailbox") as save:
                    sync_mailbox()
        save.assert_called_once_with(None, None, None, self.result, "50")

    def test_failed_refresh_does_not_commit_cursor_or_page(self) -> None:
        self.client.get_json.return_value = {"historyId": "43", "history": [{"id": "43"}]}
        with patch("app.services.mail_sync.sync_state", return_value=("me@example.com", "42", [(None, None, None)])):
            with patch("app.services.mail_sync.gmail_mailbox", side_effect=GmailAccessError("Gmail unavailable")):
                with patch("app.services.mail_sync.store_synced_mailbox") as save:
                    with patch("app.services.mail_sync.store_sync_cursor") as cursor:
                        with self.assertRaises(GmailAccessError):
                            sync_mailbox()
        save.assert_not_called()
        cursor.assert_not_called()

    def test_history_pagination_consumes_all_pages(self) -> None:
        self.client.get_json.side_effect = [
            {"historyId": "44", "history": [], "nextPageToken": "next"},
            {"historyId": "45", "history": [{"id": "45"}]},
        ]
        self.assertEqual(history_changes(self.client, "42"), (True, "45"))
        self.assertEqual(self.client.get_json.call_count, 2)


if __name__ == "__main__":
    unittest.main()
