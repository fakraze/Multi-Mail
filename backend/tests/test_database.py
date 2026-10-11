import unittest
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models.database import Account, Base, CachedMessage
from app.services.cached_mailbox import mailbox
from app.services.google_oauth import OAuthTokens
from app.services import persistence


class DatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = Path(__file__).resolve().parents[1] / "test-database.sqlite"
        self.engine = create_engine(f"sqlite:///{self.path}")
        self.session_patch = patch.object(persistence, "SessionLocal", sessionmaker(bind=self.engine))
        self.init_patch = patch.object(persistence, "initialize_database", lambda: Base.metadata.create_all(self.engine))
        self.session_patch.start()
        self.init_patch.start()
        Base.metadata.create_all(self.engine)

    def tearDown(self) -> None:
        self.session_patch.stop()
        self.init_patch.stop()
        self.engine.dispose()
        self.path.unlink(missing_ok=True)

    def test_account_tokens_and_message_survive_new_connection(self) -> None:
        persistence.store_account("one@example.com", OAuthTokens("private-access", "private-refresh"))
        result = self.mailbox_result()
        persistence.store_mailbox(None, None, None, result)
        self.engine.dispose()
        self.engine = create_engine(f"sqlite:///{self.path}")
        persistence.SessionLocal = sessionmaker(bind=self.engine)
        self.assertEqual(persistence.stored_account(),
                         ("one@example.com", OAuthTokens("private-access", "private-refresh")))
        self.assertEqual(persistence.cached_mailbox(None, None, None)["messages"][0]["id"], "message-1")
        with persistence.SessionLocal() as session:
            row = session.scalar(select(CachedMessage))
            self.assertEqual(row.thread_id, "thread-1")
            self.assertEqual(session.scalar(select(Account)).email_address, "one@example.com")

    def test_cache_miss_fetches_gmail_once_and_account_replacement_clears_cache(self) -> None:
        persistence.store_account("one@example.com", OAuthTokens("private-access", None))
        with patch("app.services.cached_mailbox.load_local_tokens", return_value=OAuthTokens("private-access", None)):
            with patch("app.services.cached_mailbox.gmail_mailbox", return_value=self.mailbox_result()) as gmail:
                first = mailbox()
                second = mailbox()
                self.assertEqual(first["messages"], second["messages"])
                gmail.assert_called_once_with(None, None, None)
                mailbox("STARRED")
                self.assertEqual(gmail.call_count, 2)
        persistence.store_account("two@example.com", OAuthTokens("other-access", None))
        self.assertIsNone(persistence.cached_mailbox(None, None, None))
        self.assertEqual(persistence.stored_account()[1].refresh_token, None)
        with persistence.SessionLocal() as session:
            self.assertEqual(session.scalars(select(CachedMessage)).all(), [])

    def test_same_account_reauthorization_keeps_existing_refresh_token(self) -> None:
        persistence.store_account("one@example.com", OAuthTokens("old-access", "private-refresh"))
        persistence.store_account("one@example.com", OAuthTokens("new-access", None))
        self.assertEqual(persistence.stored_account(),
                         ("one@example.com", OAuthTokens("new-access", "private-refresh")))

    def test_older_cached_page_without_important_is_repaired_without_gmail(self) -> None:
        persistence.store_account("one@example.com", OAuthTokens("private-access", None))
        persistence.store_mailbox(None, None, None, self.mailbox_result())
        with patch("app.services.cached_mailbox.load_local_tokens", return_value=OAuthTokens("private-access", None)):
            with patch("app.services.cached_mailbox.gmail_mailbox") as gmail:
                result = mailbox()
        self.assertEqual(result["labels"], [{"id": "IMPORTANT", "name": "Important", "kind": "system",
                                              "modifiable": True, "deletable": False}])
        gmail.assert_not_called()

    @staticmethod
    def mailbox_result() -> dict[str, object]:
        return {"account": "one@example.com", "labels": [], "next_page_token": None,
                "messages": [{"id": "message-1", "thread_id": "thread-1", "account": "one@example.com",
                              "sender": "Sender", "subject": "Subject", "snippet": "Preview",
                              "received_at": "2026-10-12T00:00:00+00:00", "starred": True,
                              "label_ids": ["INBOX", "STARRED"]}]}


if __name__ == "__main__":
    unittest.main()
