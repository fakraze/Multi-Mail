"""Read the latest authorized account's inbox without persisting Gmail data."""

import base64
import binascii
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from email.header import make_header, decode_header
from email.utils import parseaddr
from html.parser import HTMLParser
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from app.services.gmail_access import (
    ExpiredAccessError,
    GmailAccessError,
    get_profile,
    load_local_tokens,
    refresh_access_token,
)

GMAIL_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
LABELS_URL = "https://gmail.googleapis.com/gmail/v1/users/me/labels"
DISPLAY_SYSTEM_LABELS = {
    "IMPORTANT": "Important",
    "CATEGORY_PERSONAL": "Primary",
    "CATEGORY_SOCIAL": "Social",
    "CATEGORY_PROMOTIONS": "Promotions",
    "CATEGORY_UPDATES": "Updates",
    "CATEGORY_FORUMS": "Forums",
}
MESSAGE_ID = re.compile(r"^[A-Za-z0-9_-]+$")


class PlainText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.hidden += 1
        elif tag in {"br", "p", "div", "li"}:
            self.text.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.hidden:
            self.hidden -= 1
        elif tag in {"p", "div", "li"}:
            self.text.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.text.append(data)


def body_text(payload: object) -> str:
    if not isinstance(payload, dict):
        return ""
    parts = payload.get("parts")
    if isinstance(parts, list):
        for part in parts:
            if isinstance(part, dict) and part.get("mimeType") == "text/plain":
                result = body_text(part)
                if result:
                    return result
        for part in parts:
            result = body_text(part)
            if result:
                return result
    body = payload.get("body")
    encoded = body.get("data") if isinstance(body, dict) else None
    if not isinstance(encoded, str):
        return ""
    try:
        decoded = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)).decode("utf-8", errors="replace")
    except (ValueError, binascii.Error):
        return ""
    if payload.get("mimeType") == "text/html":
        parser = PlainText()
        parser.feed(decoded)
        return "".join(parser.text).strip()
    return decoded.strip()


def header_value(payload: object, name: str) -> str:
    headers = payload.get("headers") if isinstance(payload, dict) else None
    if not isinstance(headers, list):
        return ""
    for header in headers:
        if isinstance(header, dict) and str(header.get("name", "")).lower() == name.lower():
            value = header.get("value")
            if isinstance(value, str):
                try:
                    return str(make_header(decode_header(value)))
                except (UnicodeError, ValueError):
                    return value
    return ""


def sender_name(payload: object) -> str:
    value = header_value(payload, "From").strip()
    name, address = parseaddr(value)
    if name.strip():
        return name.strip().strip('"').strip()
    if address:
        return address.split("@", 1)[0].strip('"<> ') or "Unknown sender"
    return value.strip('"<> ') or "Unknown sender"


class GmailClient:
    def __init__(self) -> None:
        tokens = load_local_tokens()
        self.access_token = tokens.access_token
        self.refresh_token = tokens.refresh_token
        self.refreshed = False
        self.refresh_lock = Lock()

    def refresh(self) -> None:
        if self.refreshed or not self.refresh_token:
            raise GmailAccessError("Google access has expired. Connect Gmail again.")
        self.access_token = refresh_access_token(self.refresh_token)
        self.refreshed = True

    def profile_address(self) -> str:
        try:
            return get_profile(self.access_token).email_address
        except ExpiredAccessError:
            self.refresh()
            return get_profile(self.access_token).email_address

    def get_json(self, url: str) -> dict[str, object]:
        for attempt in range(2):
            token = self.access_token
            request = Request(url, headers={"Authorization": f"Bearer {token}"})
            try:
                with urlopen(request, timeout=10) as response:
                    data = json.load(response)
            except HTTPError as exc:
                if exc.code == 401 and attempt == 0:
                    with self.refresh_lock:
                        if token == self.access_token:
                            self.refresh()
                    continue
                if exc.code == 401:
                    raise GmailAccessError("Google access has expired. Connect Gmail again.") from exc
                if exc.code == 403:
                    raise GmailAccessError("Gmail access was denied. Check Gmail API access.") from exc
                raise GmailAccessError(f"Gmail API request failed (HTTP {exc.code}).") from exc
            except (URLError, TimeoutError, OSError, ValueError) as exc:
                raise GmailAccessError("Could not retrieve Gmail messages.") from exc
            if not isinstance(data, dict):
                raise GmailAccessError("Gmail returned an invalid response.")
            return data
        raise GmailAccessError("Could not retrieve Gmail messages.")


def summary(data: dict[str, object], account: str) -> dict[str, object]:
    message_id = data.get("id")
    timestamp = data.get("internalDate")
    if not isinstance(message_id, str) or not isinstance(timestamp, str) or not timestamp.isdecimal():
        raise GmailAccessError("Gmail returned an invalid message.")
    try:
        received_at = datetime.fromtimestamp(int(timestamp) / 1000, timezone.utc).isoformat()
    except (OverflowError, ValueError) as exc:
        raise GmailAccessError("Gmail returned an invalid message date.") from exc
    labels = data.get("labelIds")
    label_ids = labels if isinstance(labels, list) else []
    snippet = data.get("snippet")
    return {
        "id": message_id,
        "account": account,
        "sender": sender_name(data.get("payload")),
        "subject": header_value(data.get("payload"), "Subject") or "(no subject)",
        "snippet": snippet if isinstance(snippet, str) else "",
        "received_at": received_at,
        "starred": "STARRED" in label_ids,
    }


def mailbox() -> dict[str, object]:
    client = GmailClient()
    account = client.profile_address()
    label_response = client.get_json(LABELS_URL)
    raw_labels = label_response.get("labels", [])
    if not isinstance(raw_labels, list):
        raise GmailAccessError("Gmail returned invalid labels.")
    labels: list[dict[str, str]] = []
    for label in raw_labels:
        if not isinstance(label, dict):
            raise GmailAccessError("Gmail returned invalid labels.")
        label_id, name = label.get("id"), label.get("name")
        if not isinstance(label_id, str) or not isinstance(name, str):
            continue
        if label.get("type") == "user":
            labels.append({"id": label_id, "name": name})
        elif label_id in DISPLAY_SYSTEM_LABELS:
            labels.append({"id": label_id, "name": DISPLAY_SYSTEM_LABELS[label_id]})
    labels.sort(key=lambda item: item["name"].casefold())
    url = GMAIL_URL + "?" + urlencode({"labelIds": "INBOX", "maxResults": 20})
    listing = client.get_json(url)
    references = listing.get("messages", [])
    if not isinstance(references, list):
        raise GmailAccessError("Gmail returned an invalid inbox.")
    message_ids: list[str] = []
    for reference in references:
        message_id = reference.get("id") if isinstance(reference, dict) else None
        if not isinstance(message_id, str) or not MESSAGE_ID.fullmatch(message_id):
            raise GmailAccessError("Gmail returned an invalid message ID.")
        message_ids.append(message_id)

    def fetch_summary(message_id: str) -> dict[str, object]:
        detail = client.get_json(f"{GMAIL_URL}/{quote(message_id)}?format=metadata&metadataHeaders=From&metadataHeaders=Subject")
        return summary(detail, account)

    with ThreadPoolExecutor(max_workers=5) as executor:
        messages = list(executor.map(fetch_summary, message_ids))
    messages.sort(key=lambda item: str(item["received_at"]), reverse=True)
    return {"account": account, "labels": labels, "messages": messages}


def read_message(message_id: str) -> dict[str, object]:
    if not MESSAGE_ID.fullmatch(message_id):
        raise GmailAccessError("Invalid message ID.")
    client = GmailClient()
    account = client.profile_address()
    data = client.get_json(f"{GMAIL_URL}/{quote(message_id)}?format=full")
    labels = data.get("labelIds")
    if not isinstance(labels, list) or "INBOX" not in labels:
        raise GmailAccessError("This message is not in the inbox.")
    return {**summary(data, account), "body": body_text(data.get("payload")) or str(data.get("snippet", ""))}
