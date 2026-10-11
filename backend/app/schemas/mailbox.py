from typing import Literal

from pydantic import BaseModel


class MessageSummary(BaseModel):
    id: str
    account: str
    sender: str
    subject: str
    snippet: str
    received_at: str
    starred: bool
    label_ids: list[str]


class MailLabel(BaseModel):
    id: str
    name: str
    kind: Literal["user", "system"]
    modifiable: bool
    deletable: bool


class CreateLabel(BaseModel):
    account: str
    name: str


class Mailbox(BaseModel):
    account: str
    labels: list[MailLabel]
    messages: list[MessageSummary]


class MessageDetail(MessageSummary):
    body: str


class LabelChange(BaseModel):
    account: str
    label_id: str
    present: bool


class MessageLabels(BaseModel):
    id: str
    account: str
    label_ids: list[str]
    starred: bool
