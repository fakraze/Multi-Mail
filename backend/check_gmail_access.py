"""Run from backend/: python check_gmail_access.py"""

from app.services.gmail_access import GmailAccessError, verify_gmail_access


def main() -> int:
    try:
        profile = verify_gmail_access()
    except GmailAccessError as exc:
        print(f"Gmail access check failed: {exc}")
        return 1
    print(f"Gmail access verified for {profile.email_address}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
