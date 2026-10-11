"""Run from backend/: python check_gmail_modify.py MESSAGE_ID ACTION [--label-id LABEL_ID]."""

import argparse

from app.services.gmail_access import GmailAccessError
from app.services.gmail_modify import ACTIONS, modify_message


def main() -> int:
    parser = argparse.ArgumentParser(description="Modify and verify one message in the latest authorized Gmail account.")
    parser.add_argument("message_id", help="Gmail message ID from the connected inbox")
    parser.add_argument("action", choices=sorted(ACTIONS))
    parser.add_argument("--label-id", help="Gmail user-label or Important ID, required for label actions")
    args = parser.parse_args()
    try:
        modify_message(args.message_id, args.action, args.label_id)
    except GmailAccessError as exc:
        print(f"Gmail modification failed: {exc}")
        return 1
    print(f"Gmail {args.action} verified for message {args.message_id}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
