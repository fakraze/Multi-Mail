# Architecture Context

## Stack

| Layer             | Technology                | Role                           |
| ----------------- | ------------------------- | ------------------------------ |
| Frontend          | React + TypeScript + Vite | User interface                 |
| Backend           | FastAPI                   | API and business logic         |
| Auth              | Google OAuth 2.0          | Gmail account authorization    |
| Gmail Integration | Gmail API                 | Read and modify Gmail data     |
| ORM               | SQLAlchemy                | Database access                |
| Database          | SQLite                    | Local application data storage |

## System Boundaries

- `frontend/` — UI, account selection, inbox display, search, and user interactions
- `backend/app/api/` — FastAPI routes and request/response handling
- `backend/app/services/` — Gmail API, OAuth, and business logic
- `backend/app/models/` — SQLAlchemy database models
- `backend/app/schemas/` — Pydantic request and response models

## Storage Model

- **SQLite Database**: Connected Gmail accounts, OAuth credentials, and application metadata
- **Gmail**: Email content, threads, stars, labels, and mailbox state
- Full Gmail mailboxes are not permanently copied into the local database

## Auth and Access Model

- Gmail accounts are connected through Google OAuth 2.0
- Gmail passwords are never collected or stored
- OAuth credentials are stored and used only by the backend
- The frontend communicates with Gmail only through the backend
- Every Gmail operation must use the credentials of the corresponding connected account

### Local OAuth verification flow (04-google-oauth)

- The frontend navigates to `GET /auth/google/start` on the local FastAPI backend.
- The backend redirects to Google with the `gmail.modify` scope, offline access, and a random state value held in a short-lived, HTTP-only, SameSite=Lax cookie.
- Google redirects to `GET /auth/google/callback` at the configured loopback URL. The backend checks state, exchanges the authorization code, and logs only whether access and refresh tokens were returned.
- The callback displays a token-free success or error page. For the local token-storage step, the backend saves the latest authorization's access token and optional refresh token to an ignored local JSON file. Tokens are never saved to SQLite or sent to the frontend. Saving a new grant replaces the previous file, including when Google omits a refresh token. The local backend launcher disables request access logs so callback authorization codes are not logged; direct Uvicorn runs must use `--no-access-log`.
- Local configuration uses `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and a loopback `GOOGLE_REDIRECT_URI` from backend environment variables or an ignored `backend/.env` file. Environment variables take precedence. The default callback is `http://127.0.0.1:8000/auth/google/callback`; the frontend backend base URL defaults to `http://127.0.0.1:8000`.
- The local token file is `backend/oauth_tokens.json`. It is backend-only, ignored by Git, written atomically with restrictive file permissions where supported, and contains only the latest grant. It is a temporary single-account store; multi-account persistence remains a later feature.

## Invariants

1. Gmail remains the source of truth for email state
2. OAuth tokens must never be exposed to the frontend
3. Emails from different Gmail accounts must never be merged into the same thread
4. Every displayed email must preserve its source Gmail account
5. The application must not permanently store the full Gmail mailbox
6. Star and label changes must be synchronized with Gmail
