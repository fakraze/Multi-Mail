"""Backend-only check of the latest local grant against Gmail's profile API."""

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.services.google_oauth import TOKEN_FILE, TOKEN_URL, OAuthConfigError, OAuthTokens, configuration

PROFILE_URL = "https://gmail.googleapis.com/gmail/v1/users/me/profile"


class GmailAccessError(Exception):
    """A safe, credential-free message for a failed Gmail access check."""


class ExpiredAccessError(GmailAccessError):
    pass


@dataclass(frozen=True)
class GmailProfile:
    email_address: str


def load_local_tokens() -> OAuthTokens:
    try:
        data = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GmailAccessError("No local OAuth grant found. Connect Gmail first.") from exc
    except (OSError, UnicodeError, ValueError) as exc:
        raise GmailAccessError("Could not read the local OAuth grant.") from exc

    if not isinstance(data, dict) or not isinstance(data.get("access_token"), str) or not data["access_token"]:
        raise GmailAccessError("The local OAuth grant has no valid access token.")
    refresh_token = data.get("refresh_token")
    if refresh_token is not None and (not isinstance(refresh_token, str) or not refresh_token):
        raise GmailAccessError("The local OAuth grant has an invalid refresh token.")
    return OAuthTokens(data["access_token"], refresh_token)


def refresh_access_token(refresh_token: str) -> str:
    try:
        client_id, client_secret, _ = configuration()
    except OAuthConfigError as exc:
        raise GmailAccessError("Google OAuth client credentials are not configured.") from exc

    body = urlencode(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
    ).encode("ascii")
    request = Request(TOKEN_URL, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urlopen(request, timeout=10) as response:
            data = json.load(response)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        raise GmailAccessError("Could not refresh Google access. Connect Gmail again.") from exc
    if not isinstance(data, dict) or not isinstance(data.get("access_token"), str) or not data["access_token"]:
        raise GmailAccessError("Google did not return a fresh access token.")
    return data["access_token"]


def get_profile(access_token: str) -> GmailProfile:
    request = Request(PROFILE_URL, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urlopen(request, timeout=10) as response:
            data = json.load(response)
    except HTTPError as exc:
        if exc.code == 401:
            raise ExpiredAccessError("Google access has expired.") from exc
        if exc.code == 403:
            raise GmailAccessError("Gmail access was denied. Check that the Gmail API is enabled and the grant has Gmail access.") from exc
        raise GmailAccessError(f"Gmail API request failed (HTTP {exc.code}).") from exc
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        raise GmailAccessError("Could not retrieve the Gmail profile.") from exc
    if not isinstance(data, dict) or not isinstance(data.get("emailAddress"), str) or not data["emailAddress"]:
        raise GmailAccessError("Gmail returned an invalid profile.")
    return GmailProfile(data["emailAddress"])


def verify_gmail_access() -> GmailProfile:
    tokens = load_local_tokens()
    try:
        return get_profile(tokens.access_token)
    except ExpiredAccessError as exc:
        if not tokens.refresh_token:
            raise GmailAccessError("Google access has expired. Connect Gmail again.") from exc
    return get_profile(refresh_access_token(tokens.refresh_token))
