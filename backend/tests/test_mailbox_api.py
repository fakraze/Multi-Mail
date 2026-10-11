import asyncio
import unittest
from unittest.mock import patch

from app.api.mailbox import add_label, change_message_label, get_mailbox, remove_label
from app.schemas.mailbox import CreateLabel, LabelChange


class MailboxApiTests(unittest.TestCase):
    def test_filter_is_passed_to_gmail_service(self) -> None:
        with patch("app.api.mailbox.mailbox", return_value={
            "account": "me@example.com", "labels": [], "messages": [],
        }) as service:
            result = asyncio.run(get_mailbox("STARRED"))
        self.assertEqual(result.messages, [])
        service.assert_called_once_with("STARRED")

    def test_star_route_returns_confirmed_labels_and_account_scope(self) -> None:
        with patch("app.api.mailbox.modify_message", return_value={"INBOX", "STARRED"}) as service:
            result = asyncio.run(change_message_label("abc", LabelChange(
                account="me@example.com", label_id="STARRED", present=True,
            )))
        self.assertTrue(result.starred)
        self.assertEqual(result.label_ids, ["INBOX", "STARRED"])
        service.assert_called_once_with("abc", "star", None, "me@example.com", True)

    def test_create_label_route_returns_verified_label(self) -> None:
        with patch("app.api.mailbox.create_label", return_value={
            "id": "Label_123", "name": "Work", "kind": "user", "modifiable": True, "deletable": True,
        }) as service:
            result = asyncio.run(add_label(CreateLabel(account="me@example.com", name="Work")))
        self.assertEqual(result.id, "Label_123")
        service.assert_called_once_with("Work", "me@example.com")

    def test_delete_label_route_checks_account_scope(self) -> None:
        with patch("app.api.mailbox.delete_label") as service:
            asyncio.run(remove_label("Label_123", "me@example.com"))
        service.assert_called_once_with("Label_123", "me@example.com")


if __name__ == "__main__":
    unittest.main()
