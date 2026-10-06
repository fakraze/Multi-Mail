import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_SCOPE = "https://www.googleapis.com/auth/gmail.modify"
DEFAULT_REDIRECT_URI = "http://127.0.0.1:8000/auth/google/callback"
DEFAULT_FRONTEND_URL = "http://localhost:5173/"
DOTENV_FILE = Path(__file__).resolve().parents[2] / ".env"
TOKEN_FILE = Path(__file__).resolve().parents[2] / "oauth_tokens.json"


class OAuthConfigError(Exception):
    pass


class OAuthExchangeError(Exception):
    pass


class OAuthStorageError(Exception):
    pass


@dataclass(frozen=True)
class OAuthTokens:
    access_token: str
    refresh_token: str | None


def local_settings() -> dict[str, str]:
    try:
        lines = DOTENV_FILE.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return {}

    settings = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if key in {"GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REDIRECT_URI", "FRONTEND_URL"}:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            settings[key] = value
    return settings


def configuration() -> tuple[str, str, str]:
    settings = local_settings()
    client_id = os.getenv("GOOGLE_CLIENT_ID", settings.get("GOOGLE_CLIENT_ID", "")).strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", settings.get("GOOGLE_CLIENT_SECRET", "")).strip()
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", settings.get("GOOGLE_REDIRECT_URI", DEFAULT_REDIRECT_URI)).strip()
    parsed = urlsplit(redirect_uri)

    if not client_id or not client_secret:
        raise OAuthConfigError("Google OAuth client credentials are not configured.")
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
        or parsed.path != "/auth/google/callback"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise OAuthConfigError("Google OAuth redirect URI must use the local callback URL.")
    return client_id, client_secret, redirect_uri


def frontend_url() -> str:
    settings = local_settings()
    value = os.getenv("FRONTEND_URL", settings.get("FRONTEND_URL", DEFAULT_FRONTEND_URL)).strip()
    parsed = urlsplit(value)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise OAuthConfigError("Frontend URL must be a local home page URL.")
    return value.rstrip("/") + "/"


def authorization_url(client_id: str, redirect_uri: str, state: str) -> str:
    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": GMAIL_SCOPE,
            "access_type": "offline",
            "state": state,
        }
    )
    return f"{AUTHORIZATION_URL}?{query}"


def exchange_code(code: str, client_id: str, client_secret: str, redirect_uri: str) -> OAuthTokens:
    body = urlencode(
        {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode("ascii")
    request = Request(
        TOKEN_URL,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            tokens = json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
        raise OAuthExchangeError("Google token exchange failed.") from exc

    if not isinstance(tokens, dict) or not isinstance(tokens.get("access_token"), str) or not tokens["access_token"]:
        raise OAuthExchangeError("Google did not return an access token.")
    refresh_token = tokens.get("refresh_token")
    return OAuthTokens(
        access_token=tokens["access_token"],
        refresh_token=refresh_token if isinstance(refresh_token, str) and refresh_token else None,
    )


def save_tokens(tokens: OAuthTokens) -> None:
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=TOKEN_FILE.parent,
            prefix=".oauth_tokens-",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            os.chmod(temporary_path, 0o600)
            json.dump(
                {"access_token": tokens.access_token, "refresh_token": tokens.refresh_token},
                temporary_file,
            )
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, TOKEN_FILE)
    except OSError as exc:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise OAuthStorageError("Could not save Google OAuth tokens.") from exc
