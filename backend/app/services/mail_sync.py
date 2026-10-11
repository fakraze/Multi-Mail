"""Bounded Gmail history synchronization for the local single-account cache."""

from threading import Lock
from urllib.parse import urlencode

from sqlalchemy.exc import SQLAlchemyError

from app.services.gmail_access import GmailAccessError, load_local_tokens
from app.services.gmail_inbox import GmailClient, mailbox as gmail_mailbox
from app.services.google_oauth import OAuthStorageError
from app.services.persistence import cache_key, store_sync_cursor, store_synced_mailbox, sync_state

PROFILE_URL = "https://gmail.googleapis.com/gmail/v1/users/me/profile"
HISTORY_URL = "https://gmail.googleapis.com/gmail/v1/users/me/history"
sync_lock = Lock()


def valid_history_id(value: object) -> str:
    if not isinstance(value, str) or not value.isdecimal():
        raise GmailAccessError("Gmail returned an invalid history cursor.")
    return value


def sync_mailbox(label: str | None = None, query: str | None = None,
                 token: str | None = None) -> None:
    if query is not None and (not query.strip() or label is not None):
        raise GmailAccessError("Invalid mailbox search.")
    if token is not None and (not token.strip() or len(token) > 4096):
        raise GmailAccessError("Invalid page token.")
    with sync_lock:
        load_local_tokens()
        try:
            address, cursor, pages = sync_state()
            client = GmailClient()
            if client.profile_address() != address:
                raise GmailAccessError("The connected Gmail account changed. Refresh the page.")
            if cursor and cache_key(label, query, token) in {
                cache_key(*page) for page in pages
            }:
                try:
                    changed, latest = history_changes(client, cursor)
                except GmailAccessError:
                    pass  # The history cursor cannot be used; rebuild the requested page.
                else:
                    if not changed:
                        store_sync_cursor(address, latest)
                        return
                    result = gmail_mailbox(label, query, token)
                    store_synced_mailbox(label, query, token, result, latest)
                    return
            profile = client.get_json(PROFILE_URL)
            latest = valid_history_id(profile.get("historyId"))
            result = gmail_mailbox(label, query, token)
            store_synced_mailbox(label, query, token, result, latest)
        except OAuthStorageError as exc:
            raise GmailAccessError(str(exc)) from exc
        except (OSError, SQLAlchemyError, ValueError) as exc:
            raise GmailAccessError("Could not synchronize the local mail cache.") from exc


def history_changes(client: GmailClient, cursor: str) -> tuple[bool, str]:
    changed = False
    page_token: str | None = None
    seen: set[str] = set()
    while True:
        params = [("startHistoryId", cursor), ("maxResults", "500")]
        if page_token:
            params.append(("pageToken", page_token))
        data = client.get_json(HISTORY_URL + "?" + urlencode(params))
        latest = valid_history_id(data.get("historyId"))
        entries = data.get("history", [])
        if not isinstance(entries, list):
            raise GmailAccessError("Gmail returned invalid mail history.")
        changed = changed or bool(entries)
        next_token = data.get("nextPageToken")
        if next_token is None:
            return changed, latest
        if not isinstance(next_token, str) or not next_token or next_token in seen:
            raise GmailAccessError("Gmail returned invalid mail history pagination.")
        seen.add(next_token)
        page_token = next_token
