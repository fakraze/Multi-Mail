"""Modify one message in the latest authorized Gmail account and verify it."""

from urllib.parse import quote

from app.services.gmail_access import GmailAccessError
from app.services.gmail_inbox import DISPLAY_SYSTEM_LABELS, GMAIL_URL, LABELS_URL, MESSAGE_ID, GmailClient

ACTIONS = {"star", "unstar", "add-label", "remove-label"}


def message_labels(client: GmailClient, message_id: str) -> set[str]:
    data = client.get_json(f"{GMAIL_URL}/{quote(message_id)}?format=minimal")
    if data.get("id") != message_id:
        raise GmailAccessError("Gmail returned a different message.")
    labels = data.get("labelIds", [])
    if not isinstance(labels, list) or not all(isinstance(label, str) for label in labels):
        raise GmailAccessError("Gmail returned invalid message labels.")
    return set(labels)


def check_modifiable_label(client: GmailClient, label_id: str) -> None:
    if not MESSAGE_ID.fullmatch(label_id):
        raise GmailAccessError("Invalid label ID.")
    if label_id == "IMPORTANT":
        return
    data = client.get_json(LABELS_URL)
    labels = data.get("labels", [])
    if not isinstance(labels, list):
        raise GmailAccessError("Gmail returned invalid labels.")
    if not any(
        isinstance(label, dict) and label.get("id") == label_id
        and (label.get("type") == "user" or label_id in DISPLAY_SYSTEM_LABELS and label.get("type") == "system")
        for label in labels
    ):
        raise GmailAccessError("The label cannot be edited in this Gmail account.")


def create_label(name: str, expected_account: str) -> dict[str, object]:
    clean_name = name.strip()
    if not clean_name or len(clean_name) > 225 or any(ord(char) < 32 for char in clean_name):
        raise GmailAccessError("Invalid label name.")
    client = GmailClient()
    if client.profile_address() != expected_account:
        raise GmailAccessError("The connected Gmail account changed. Refresh the page.")
    existing = client.get_json(LABELS_URL).get("labels", [])
    if not isinstance(existing, list):
        raise GmailAccessError("Gmail returned invalid labels.")
    if any(isinstance(label, dict) and isinstance(label.get("name"), str)
           and label["name"].casefold() == clean_name.casefold() for label in existing):
        raise GmailAccessError("A Gmail label with this name already exists.")
    created = client.post_json(LABELS_URL, {
        "name": clean_name, "labelListVisibility": "labelShow", "messageListVisibility": "show",
    })
    label_id = created.get("id")
    if not isinstance(label_id, str) or not MESSAGE_ID.fullmatch(label_id):
        raise GmailAccessError("Gmail returned an invalid new label.")
    confirmed = client.get_json(LABELS_URL).get("labels", [])
    if not isinstance(confirmed, list) or not any(
        isinstance(label, dict) and label.get("id") == label_id
        and label.get("name") == clean_name and label.get("type") == "user"
        for label in confirmed
    ):
        raise GmailAccessError("Gmail did not confirm the new label.")
    return {"id": label_id, "name": clean_name, "kind": "user", "modifiable": True, "deletable": True}


def delete_label(label_id: str, expected_account: str) -> None:
    if not MESSAGE_ID.fullmatch(label_id):
        raise GmailAccessError("Invalid label ID.")
    client = GmailClient()
    if client.profile_address() != expected_account:
        raise GmailAccessError("The connected Gmail account changed. Refresh the page.")
    labels = client.get_json(LABELS_URL).get("labels", [])
    if not isinstance(labels, list):
        raise GmailAccessError("Gmail returned invalid labels.")
    if not any(isinstance(label, dict) and label.get("id") == label_id and label.get("type") == "user"
               for label in labels):
        raise GmailAccessError("Only Gmail user labels can be deleted.")
    client.delete_json(f"{LABELS_URL}/{quote(label_id)}")
    confirmed = client.get_json(LABELS_URL).get("labels", [])
    if not isinstance(confirmed, list) or any(
        isinstance(label, dict) and label.get("id") == label_id for label in confirmed
    ):
        raise GmailAccessError("Gmail did not confirm label deletion.")


def modify_message(
    message_id: str,
    action: str,
    label_id: str | None = None,
    expected_account: str | None = None,
    inbox_only: bool = False,
) -> set[str]:
    if not MESSAGE_ID.fullmatch(message_id):
        raise GmailAccessError("Invalid message ID.")
    if action not in ACTIONS:
        raise GmailAccessError("Invalid Gmail action.")
    if action in {"add-label", "remove-label"} and not label_id:
        raise GmailAccessError("A label ID is required for this action.")
    if action in {"star", "unstar"} and label_id is not None:
        raise GmailAccessError("A label ID is only valid for label actions.")

    client = GmailClient()
    if expected_account is not None and client.profile_address() != expected_account:
        raise GmailAccessError("The connected Gmail account changed. Refresh the page.")
    target_label = "STARRED" if action in {"star", "unstar"} else label_id
    if target_label != "STARRED":
        check_modifiable_label(client, target_label)

    before = message_labels(client, message_id)
    if inbox_only and "INBOX" not in before:
        raise GmailAccessError("This message is not in the inbox.")
    adding = action in {"star", "add-label"}
    body = {
        "addLabelIds": [target_label] if adding else [],
        "removeLabelIds": [] if adding else [target_label],
    }
    result = client.post_json(f"{GMAIL_URL}/{quote(message_id)}/modify", body)
    if result.get("id") != message_id:
        raise GmailAccessError("Gmail returned a different message after modification.")
    labels = message_labels(client, message_id)
    if (target_label in labels) != adding:
        raise GmailAccessError("Gmail did not confirm the requested message change.")
    return labels
