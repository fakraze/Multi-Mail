from asyncio import to_thread

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.mailbox import CreateLabel, LabelChange, MailLabel, Mailbox, MessageDetail, MessageLabels
from app.services.gmail_access import GmailAccessError
from app.services.cached_mailbox import mailbox
from app.services.gmail_inbox import read_message
from app.services.gmail_modify import create_label, delete_label, modify_message
from app.services.google_oauth import OAuthStorageError
from app.services.persistence import invalidate_mailbox_cache, store_confirmed_message_labels
from app.services.mail_sync import sync_mailbox

router = APIRouter(prefix="/api")


async def clear_cached_pages() -> None:
    try:
        await to_thread(invalidate_mailbox_cache)
    except (OSError, SQLAlchemyError) as exc:
        raise HTTPException(status_code=500, detail="Could not update the local mail cache.") from exc


def api_error(exc: GmailAccessError) -> HTTPException:
    message = str(exc)
    status = 401 if "Connect Gmail" in message else 400 if message.startswith("Invalid ") else 409 if message in {
        "The connected Gmail account changed. Refresh the page.", "This message is not in the inbox.",
        "A Gmail label with this name already exists."
    } else 502
    return HTTPException(status_code=status, detail=message)


@router.get("/mailbox", response_model=Mailbox)
async def get_mailbox(label_id: str | None = Query(default=None), q: str | None = Query(default=None),
                      page_token: str | None = Query(default=None)) -> Mailbox:
    try:
        return Mailbox.model_validate(await to_thread(mailbox, label_id, q, page_token))
    except GmailAccessError as exc:
        raise api_error(exc) from exc


@router.post("/mailbox/sync", status_code=204)
async def sync_mailbox_route(label_id: str | None = Query(default=None), q: str | None = Query(default=None),
                             page_token: str | None = Query(default=None)) -> None:
    try:
        await to_thread(sync_mailbox, label_id, q, page_token)
    except GmailAccessError as exc:
        raise api_error(exc) from exc


@router.get("/messages/{message_id}", response_model=MessageDetail)
async def get_message(message_id: str) -> MessageDetail:
    try:
        return MessageDetail.model_validate(await to_thread(read_message, message_id))
    except GmailAccessError as exc:
        raise api_error(exc) from exc


@router.patch("/messages/{message_id}/labels", response_model=MessageLabels)
async def change_message_label(message_id: str, change: LabelChange) -> MessageLabels:
    action = ("star" if change.present else "unstar") if change.label_id == "STARRED" else (
        "add-label" if change.present else "remove-label"
    )
    label_id = None if change.label_id == "STARRED" else change.label_id
    try:
        labels = await to_thread(modify_message, message_id, action, label_id, change.account, True)
    except GmailAccessError as exc:
        raise api_error(exc) from exc
    try:
        await to_thread(store_confirmed_message_labels, change.account, message_id, labels)
    except (OSError, SQLAlchemyError, OAuthStorageError) as exc:
        raise HTTPException(status_code=500, detail="Could not update the local mail cache.") from exc
    return MessageLabels(id=message_id, account=change.account, label_ids=sorted(labels), starred="STARRED" in labels)


@router.post("/labels", response_model=MailLabel)
async def add_label(request: CreateLabel) -> MailLabel:
    try:
        result = MailLabel.model_validate(await to_thread(create_label, request.name, request.account))
    except GmailAccessError as exc:
        raise api_error(exc) from exc
    await clear_cached_pages()
    return result


@router.delete("/labels/{label_id}", status_code=204)
async def remove_label(label_id: str, account: str = Query()) -> None:
    try:
        await to_thread(delete_label, label_id, account)
    except GmailAccessError as exc:
        raise api_error(exc) from exc
    await clear_cached_pages()
