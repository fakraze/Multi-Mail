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
- The callback displays a token-free error page on failure. On success, it saves the latest authorization's access token and optional refresh token to an ignored local JSON file, then redirects to the configured frontend home page. Tokens are never saved to SQLite or sent to the frontend. Saving a new grant replaces the previous file, including when Google omits a refresh token. The local backend launcher disables request access logs so callback authorization codes are not logged; direct Uvicorn runs must use `--no-access-log`.
- Local configuration uses `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, a loopback `GOOGLE_REDIRECT_URI`, and a loopback `FRONTEND_URL` from backend environment variables or an ignored `backend/.env` file. Environment variables take precedence. The default callback is `http://127.0.0.1:8000/auth/google/callback`; the frontend home URL defaults to `http://localhost:5173/`, and its backend base URL defaults to `http://127.0.0.1:8000`.
- The local token file is `backend/oauth_tokens.json`. It is backend-only, ignored by Git, written atomically with restrictive file permissions where supported, and contains only the latest grant. It is a temporary single-account store; multi-account persistence remains a later feature.

### Gmail access verification (05-gmail-access)

- A backend-only command reads the latest local OAuth grant and calls Gmail `users.getProfile` for `me`. The existing `gmail.modify` grant authorizes this call and is also required by the planned star and label actions; no additional scope is requested.
- If Gmail rejects an expired access token, the command can exchange the saved refresh token for a fresh access token and retry once. Refreshed tokens and Gmail profile data are not persisted. The command prints the verified account address locally and handles API errors without exposing credentials.

### Live single-account inbox (05b-live-inbox)

- The default frontend home URL renders the original sample mailbox without requesting live Gmail data, even if an older local grant exists. A successful OAuth callback redirects to that URL with a non-secret `gmail=connected` query marker; the frontend then renders the live mailbox. Error callbacks continue to render backend error pages. The redirect carries no token or Gmail data.
- The frontend calls backend `GET /api/mailbox` for the latest grant's Gmail account address, user-created and category/Important label names, and up to 20 newest INBOX messages. The backend turns each `From` header into a display name, using the address's local part when no name is supplied. `GET /api/messages/{message_id}` returns one INBOX message as plain text for reading. The backend is the only Gmail API caller; responses never contain credentials. Connected-page controls retain the sample layout; unfinished Gmail actions display an unavailable notice and do not modify Gmail.
- Both endpoints read the latest local grant and may refresh an expired access token in memory. Gmail content and refreshed access tokens are not persisted. This phase remains a single-account local flow; the latest OAuth grant replaces the previous account.
- Local development allows the configured frontend origin to call the backend API. The frontend origin is a fixed loopback URL from backend configuration, never a redirect target supplied by a request.

## Invariants

1. Gmail remains the source of truth for email state
2. OAuth tokens must never be exposed to the frontend
3. Emails from different Gmail accounts must never be merged into the same thread
4. Every displayed email must preserve its source Gmail account
5. The application must not permanently store the full Gmail mailbox
6. Star and label changes must be synchronized with Gmail
