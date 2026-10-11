"""Read a requested mailbox page from SQLite or fill it from Gmail once."""

from app.services.gmail_access import GmailAccessError, load_local_tokens
from app.services.gmail_inbox import mailbox as gmail_mailbox, with_important_label
from app.services.google_oauth import OAuthStorageError
from app.services.persistence import cached_mailbox, store_mailbox
from sqlalchemy.exc import SQLAlchemyError


def mailbox(label: str | None = None, query: str | None = None,
            token: str | None = None) -> dict[str, object]:
    if query is not None and (not query.strip() or label is not None):
        raise GmailAccessError("Invalid mailbox search.")
    if token is not None and (not token.strip() or len(token) > 4096):
        raise GmailAccessError("Invalid page token.")
    load_local_tokens()
    try:
        cached = cached_mailbox(label, query, token)
    except (OSError, SQLAlchemyError, ValueError) as exc:
        raise GmailAccessError("Could not read the local mail cache.") from exc
    if cached is not None:
        cached["labels"] = with_important_label(cached["labels"])
        return cached
    result = gmail_mailbox(label, query, token)
    result["labels"] = with_important_label(result["labels"])
    try:
        store_mailbox(label, query, token, result)
    except OAuthStorageError as exc:
        raise GmailAccessError(str(exc)) from exc
    except (OSError, SQLAlchemyError, ValueError) as exc:
        raise GmailAccessError("Could not save the local mail cache.") from exc
    return result
