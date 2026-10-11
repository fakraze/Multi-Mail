"""Single-account credential storage and mailbox page read cache."""

import json

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError

from app.models.database import Account, CachedMessage, CachedPage, SessionLocal, initialize_database
from app.services.google_oauth import OAuthStorageError, OAuthTokens


def store_account(address: str, tokens: OAuthTokens) -> None:
    if not address or not tokens.access_token:
        raise OAuthStorageError("Could not save Google OAuth tokens.")
    try:
        initialize_database()
        with SessionLocal.begin() as session:
            previous = session.scalar(select(Account).limit(1))
            refresh_token = tokens.refresh_token or (
                previous.refresh_token if previous is not None and previous.email_address == address else None
            )
            session.execute(delete(CachedPage))
            session.execute(delete(CachedMessage))
            session.execute(delete(Account))
            session.add(Account(email_address=address, access_token=tokens.access_token,
                                refresh_token=refresh_token))
    except (OSError, SQLAlchemyError) as exc:
        raise OAuthStorageError("Could not save Google OAuth tokens.") from exc


def stored_account() -> tuple[str, OAuthTokens] | None:
    initialize_database()
    with SessionLocal() as session:
        account = session.scalar(select(Account).limit(1))
        if account is None:
            return None
        return account.email_address, OAuthTokens(account.access_token, account.refresh_token)


def cache_key(label: str | None, query: str | None, token: str | None) -> str:
    return json.dumps([label, query, token], separators=(",", ":"))


def cached_mailbox(label: str | None, query: str | None, token: str | None) -> dict[str, object] | None:
    initialize_database()
    with SessionLocal() as session:
        account = session.scalar(select(Account).limit(1))
        if account is None:
            return None
        page = session.get(CachedPage, (account.id, cache_key(label, query, token)))
        if page is None:
            return None
        messages = []
        for message_id in json.loads(page.message_ids_json):
            row = session.get(CachedMessage, (account.id, message_id))
            if row is None:
                return None
            messages.append({"id": row.gmail_id, "thread_id": row.thread_id, "account": account.email_address,
                             "sender": row.sender, "subject": row.subject, "snippet": row.snippet,
                             "received_at": row.received_at, "starred": row.starred,
                             "label_ids": json.loads(row.label_ids_json)})
        return {"account": account.email_address, "labels": json.loads(page.labels_json),
                "messages": messages, "next_page_token": page.next_page_token}


def store_mailbox(label: str | None, query: str | None, token: str | None,
                  result: dict[str, object]) -> None:
    initialize_database()
    with SessionLocal.begin() as session:
        account = session.scalar(select(Account).limit(1))
        if account is None or account.email_address != result["account"]:
            raise OAuthStorageError("The connected Gmail account changed. Refresh the page.")
        messages = result["messages"]
        for item in messages:
            row = session.get(CachedMessage, (account.id, item["id"]))
            if row is None:
                row = CachedMessage(account_id=account.id, gmail_id=item["id"])
                session.add(row)
            row.thread_id = item["thread_id"]
            row.sender = item["sender"]
            row.subject = item["subject"]
            row.snippet = item["snippet"]
            row.received_at = item["received_at"]
            row.starred = item["starred"]
            row.label_ids_json = json.dumps(item["label_ids"])
        key = cache_key(label, query, token)
        page = session.get(CachedPage, (account.id, key))
        if page is None:
            page = CachedPage(account_id=account.id, cache_key=key)
            session.add(page)
        page.message_ids_json = json.dumps([item["id"] for item in messages])
        page.labels_json = json.dumps(result["labels"])
        page.next_page_token = result["next_page_token"]


def sync_state() -> tuple[str, str | None, list[tuple[str | None, str | None, str | None]]]:
    initialize_database()
    with SessionLocal() as session:
        account = session.scalar(select(Account).limit(1))
        if account is None:
            raise OAuthStorageError("No local OAuth grant found. Connect Gmail first.")
        pages = session.scalars(select(CachedPage).where(CachedPage.account_id == account.id)).all()
        return account.email_address, account.history_id, [tuple(json.loads(page.cache_key)) for page in pages]


def store_sync_cursor(address: str, history_id: str) -> None:
    initialize_database()
    with SessionLocal.begin() as session:
        account = session.scalar(select(Account).limit(1))
        if account is None or account.email_address != address:
            raise OAuthStorageError("The connected Gmail account changed. Refresh the page.")
        account.history_id = history_id


def store_synced_mailbox(label: str | None, query: str | None, token: str | None,
                         result: dict[str, object], history_id: str) -> None:
    initialize_database()
    with SessionLocal.begin() as session:
        account = session.scalar(select(Account).limit(1))
        if account is None or account.email_address != result["account"]:
            raise OAuthStorageError("The connected Gmail account changed. Refresh the page.")
        session.execute(delete(CachedPage).where(CachedPage.account_id == account.id))
        for item in result["messages"]:
            row = session.get(CachedMessage, (account.id, item["id"]))
            if row is None:
                row = CachedMessage(account_id=account.id, gmail_id=item["id"])
                session.add(row)
            row.thread_id = item["thread_id"]
            row.sender = item["sender"]
            row.subject = item["subject"]
            row.snippet = item["snippet"]
            row.received_at = item["received_at"]
            row.starred = item["starred"]
            row.label_ids_json = json.dumps(item["label_ids"])
        session.add(CachedPage(account_id=account.id, cache_key=cache_key(label, query, token),
                               message_ids_json=json.dumps([item["id"] for item in result["messages"]]),
                               labels_json=json.dumps(result["labels"]),
                               next_page_token=result["next_page_token"]))
        account.history_id = history_id


def invalidate_mailbox_cache() -> None:
    initialize_database()
    with SessionLocal.begin() as session:
        session.execute(delete(CachedPage))
