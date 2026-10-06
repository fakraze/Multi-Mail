from pydantic import BaseModel


class MessageSummary(BaseModel):
    id: str
    account: str
    sender: str
    subject: str
    snippet: str
    received_at: str
    starred: bool


class MailLabel(BaseModel):
    id: str
    name: str


class Mailbox(BaseModel):
    account: str
    labels: list[MailLabel]
    messages: list[MessageSummary]


class MessageDetail(MessageSummary):
    body: str
