from asyncio import to_thread

from fastapi import APIRouter, HTTPException

from app.schemas.mailbox import Mailbox, MessageDetail
from app.services.gmail_access import GmailAccessError
from app.services.gmail_inbox import mailbox, read_message

router = APIRouter(prefix="/api")


def api_error(exc: GmailAccessError) -> HTTPException:
    message = str(exc)
    status = 401 if "Connect Gmail" in message else 400 if message == "Invalid message ID." else 502
    return HTTPException(status_code=status, detail=message)


@router.get("/mailbox", response_model=Mailbox)
async def get_mailbox() -> Mailbox:
    try:
        return Mailbox.model_validate(await to_thread(mailbox))
    except GmailAccessError as exc:
        raise api_error(exc) from exc


@router.get("/messages/{message_id}", response_model=MessageDetail)
async def get_message(message_id: str) -> MessageDetail:
    try:
        return MessageDetail.model_validate(await to_thread(read_message, message_id))
    except GmailAccessError as exc:
        raise api_error(exc) from exc
