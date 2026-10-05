import logging
import secrets
from asyncio import to_thread

from fastapi import APIRouter, Cookie, Query
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app.services.google_oauth import (
    OAuthConfigError,
    OAuthExchangeError,
    authorization_url,
    configuration,
    exchange_code,
)

router = APIRouter(prefix="/auth/google")
# Uvicorn configures this logger at INFO; its access logger remains disabled by the local launch command.
logger = logging.getLogger("uvicorn.error")
STATE_COOKIE = "google_oauth_state"


def result_page(message: str, status_code: int) -> HTMLResponse:
    response = HTMLResponse(
        f"<!doctype html><html lang='en'><meta charset='utf-8'>"
        f"<title>Multi Mail Google connection</title><body><h1>{message}</h1>"
        "<p>You can return to Multi Mail.</p></body></html>",
        status_code=status_code,
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@router.get("/start")
def start() -> Response:
    try:
        client_id, _, redirect_uri = configuration()
    except OAuthConfigError:
        return result_page("Google connection is not configured.", 503)

    state = secrets.token_urlsafe(32)
    response = RedirectResponse(authorization_url(client_id, redirect_uri, state))
    response.set_cookie(
        STATE_COOKIE,
        state,
        max_age=600,
        path="/auth/google/callback",
        httponly=True,
        samesite="lax",
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@router.get("/callback")
async def callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    saved_state: str | None = Cookie(default=None, alias=STATE_COOKIE),
) -> HTMLResponse:
    if not state or not saved_state or not secrets.compare_digest(state, saved_state):
        response = result_page("Google connection could not be verified.", 400)
    elif error:
        response = result_page("Google connection was not approved.", 400)
    elif not code:
        response = result_page("Google did not return an authorization code.", 400)
    else:
        try:
            client_id, client_secret, redirect_uri = configuration()
            has_refresh_token = await to_thread(exchange_code, code, client_id, client_secret, redirect_uri)
        except OAuthConfigError:
            response = result_page("Google connection is not configured.", 503)
        except OAuthExchangeError:
            logger.warning("Google OAuth token exchange failed")
            response = result_page("Google connection failed. Please try again.", 502)
        else:
            logger.info("Google OAuth token exchange succeeded: access_token=True refresh_token=%s", has_refresh_token)
            response = result_page("Google authorization verified. No account was saved yet.", 200)

    response.delete_cookie(STATE_COOKIE, path="/auth/google/callback", samesite="lax")
    return response
