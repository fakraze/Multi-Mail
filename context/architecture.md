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

### Single-account database cache (09-database)

- `backend/mail.db` is an ignored local SQLite database accessed only through SQLAlchemy in the backend. It holds one connected account, its access and optional refresh token, cached message summaries with Gmail thread IDs, and requested mailbox pages. Reauthorizing replaces the account and clears cached pages and messages. A same-account grant that omits a refresh token retains the prior refresh token; a different account never inherits it. Credentials remain local plaintext and must be protected by local filesystem access.
- A mailbox page is keyed by its label or search query and Gmail page token. Its stored ordered message IDs, sidebar labels, and next-page token preserve the existing API response. An existing page, including an empty page, is returned without a Gmail call. A missing page is fetched from Gmail and committed with its messages before returning. Individual message bodies continue to be read from Gmail and are not cached.
- Gmail edits invalidate cached mailbox pages so later reads fetch Gmail state; this does not synchronize or refresh mail automatically. Cached message rows may be replaced on a later page miss. Gmail remains authoritative.
- The existing `backend/oauth_tokens.json` is a legacy single-grant store. On first access it can be migrated to SQLite after Gmail profile verification, then removed. New OAuth callbacks identify the granted Gmail address before saving the account and credentials to SQLite. Refreshed access tokens are not persisted.

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
- The historical local token file was `backend/oauth_tokens.json`. Feature 09 replaces it with `backend/mail.db`; the old file is read only for one-time migration.

### Gmail access verification (05-gmail-access)

- A backend-only command reads the latest local OAuth grant and calls Gmail `users.getProfile` for `me`. The existing `gmail.modify` grant authorizes this call and is also required by the planned star and label actions; no additional scope is requested.
- If Gmail rejects an expired access token, the command can exchange the saved refresh token for a fresh access token and retry once. Refreshed tokens and Gmail profile data are not persisted. The command prints the verified account address locally and handles API errors without exposing credentials.

### Live single-account inbox (05b-live-inbox)

- The default frontend home URL renders the original sample mailbox without requesting live Gmail data, even if an older local grant exists. A successful OAuth callback redirects to that URL with a non-secret `gmail=connected` query marker; the frontend then renders the live mailbox. Error callbacks continue to render backend error pages. The redirect carries no token or Gmail data.
- The frontend calls backend `GET /api/mailbox` for the latest grant's Gmail account address, user-created and category/Important label names, and up to 20 newest INBOX messages. The backend turns each `From` header into a display name, using the address's local part when no name is supplied. `GET /api/messages/{message_id}` returns one INBOX message as plain text for reading. The backend is the only Gmail API caller; responses never contain credentials. Connected-page controls retain the sample layout; unfinished Gmail actions display an unavailable notice and do not modify Gmail.
- Both endpoints read the latest local grant and may refresh an expired access token in memory. Gmail content and refreshed access tokens are not persisted. This phase remains a single-account local flow; the latest OAuth grant replaces the previous account.
- Local development allows the configured frontend origin to call the backend API. The frontend origin is a fixed loopback URL from backend configuration, never a redirect target supplied by a request.

### Backend Gmail state modification (06-gmail-modify)

- A backend-only command accepts one explicit Gmail message ID and one action: star, unstar, add-label, or remove-label. Label actions additionally require an ID for a user label, Important, or a displayed Gmail category; the command checks it against the authorized account's labels. Other system labels remain unavailable to avoid changing read/unread or unrelated mailbox state.
- The command reads the latest grant from backend storage, refreshes an expired access token in memory if possible, and calls Gmail `users.messages.modify` with only the requested label change. It reads the same message again and reports success only when that message ID and label state match the request.
- Gmail remains the sole store of message state. No modification route or frontend action contract is introduced in this backend verification unit.

### Connected-page Gmail actions and filters (06b-gmail-modify-ui)

- `GET /api/mailbox?label_id=...` returns up to 20 newest INBOX messages that also have the requested Gmail label. Omit `label_id` for Inbox; use `STARRED` for Starred, or an ID from the returned sidebar labels. The response includes each message's `label_ids` and each sidebar label's `modifiable` and `deletable` flags. Displayed user and category labels and Important are modifiable; only user labels are deletable.
- `PATCH /api/messages/{message_id}/labels` accepts `{account, label_id, present}`. The backend verifies the latest authorized Gmail account matches `account`, checks that the message is still in INBOX, permits `STARRED`, user labels, Important, or displayed categories, calls Gmail modify for only that label, and reads the same message back. It returns `{id, account, label_ids, starred}` only after confirmation. Errors are returned without tokens or message content.
- The connected frontend uses this route for star and label checkboxes, and reads the Gmail-filtered mailbox when Inbox, Starred, or a sidebar label is selected. Only the latest single-account grant is supported; the sample page remains local sample data.

### Connected-page label creation and category editing (06c-gmail-labels)

- All labels displayed in the live sidebar are editable on an INBOX message: Gmail user labels, Important, and the five Gmail category labels. The backend still rejects system labels that would change read/unread, archive, spam, trash, sent, or draft state.
- `POST /api/labels` accepts `{account, name}`. The backend checks the latest authorized account, creates a Gmail user label with `users.labels.create`, reads the label list again to verify the new ID and name, and returns `{id, name, kind: user, modifiable: true, deletable: true}`. The frontend adds it to the sidebar and message label picker. Gmail remains the only store; the application database is unchanged.

### Connected-page label deletion (06d-gmail-label-delete)

- Mailbox label entries expose `deletable: true` only for Gmail user labels. The live sidebar shows a delete button only for those entries and asks for confirmation that the label will be removed from Gmail messages; deleting a label does not delete messages.
- `DELETE /api/labels/{label_id}?account=...` checks the latest authorized account and verifies that the requested ID is a user label before calling Gmail `users.labels.delete`. It reads the Gmail label list again and reports success only when that ID is absent. The frontend removes the deleted label from its sidebar and local message state, and returns to Inbox if that label was the active filter.

### Gmail category navigation and Purchases view (06e-gmail-categories)

- Gmail `CATEGORY_PERSONAL` is the built-in Primary classification label. The category names shown by the app are in English. The Categories sidebar shows five entries: Purchases, Social, Updates, Forums, and Promotions; it omits Primary. Gmail's five `CATEGORY_*` labels remain available in the API and message label picker for filtering or manual application where applicable. Important remains a separate system marker. User-created labels appear in their own sidebar group.
- Gmail Purchases is a view without a label ID in `users.labels.list`. The mailbox response adds a virtual `PURCHASES` entry with `kind: view`, `modifiable: false`, and `deletable: false`. `GET /api/mailbox?label_id=PURCHASES` queries Gmail `users.messages.list` with `labelIds=INBOX` and `q=category:purchases`; it returns the same message summary format and up to 20 matches. This virtual entry cannot be sent to the label modify or delete routes.
- Each mailbox label entry exposes `kind: user | system | view`. The connected sidebar uses this to group categories, Important, and user labels without treating Purchases as a Gmail label. It filters `CATEGORY_PERSONAL` from the Categories group so the group has exactly five visible entries when Gmail returns the four other category labels. The message label picker includes only modifiable entries.

### Labels and Important only (06g-labels-only)

- The current connected mailbox exposes only Gmail user-created labels and the Important system label as selectable labels. The sidebar contains Inbox, Starred, Important, and user Labels; there is no Categories group or Purchases view. Gmail category IDs may still exist on messages as Gmail state, but they are not presented as app labels.
- `GET /api/mailbox` returns only user labels and Important in its `labels` array. A `label_id` filter accepts `STARRED`, `IMPORTANT`, or a returned user label ID. Category and Purchases filters are invalid. `PATCH /api/messages/{message_id}/labels` accepts star changes, Important, or user label IDs; it rejects category IDs. The backend-only modify command follows the same label rule.
- Important is a fixed supported Gmail system marker. The connected sidebar shows it immediately, and every mailbox response includes its label metadata even if Gmail omits it from `users.labels.list` or an older cached page lacks it.
- The message label dialog lists Important and user labels only. When none of those are applied to a message, it says `No labels applied.` even if Gmail reports a category such as `CATEGORY_PERSONAL`. Its checkboxes still let the user add Important or a user label.

### Single-account Gmail search (07-gmail-search)

- `GET /api/mailbox?q=...` uses the latest local OAuth grant and passes the nonblank query as Gmail `users.messages.list` `q` without adding an INBOX filter. Search and `label_id` filtering are mutually exclusive. It returns up to 20 matching messages in the existing mailbox response shape, including the source account and sidebar labels. Search results remain in Gmail only.
- The connected page submits one free-text search field to this endpoint. Search results replace the mail list; choosing a folder clears the active search, and Refresh reruns the active query. A blank submission returns to Inbox.
- `GET /api/messages/{message_id}` may read a search result outside INBOX as plain text. Label modifications still require INBOX, so Gmail state cannot be changed through search for a message outside INBOX.

### Single-account mail pagination (08-mail-pagination)

- `GET /api/mailbox` accepts an optional Gmail `page_token` alongside its existing label or search query. It requests at most 50 message references from Gmail and returns `next_page_token` (null when Gmail supplies none) with the existing account, labels, and message summaries. Invalid page tokens and Gmail API failures use controlled API errors.
- The connected page starts at page 1 and keeps only the Gmail token for each visited page in memory. Next uses the returned token; Previous reuses the token saved for that page. Changing the folder or search and refreshing the list reset pagination to page 1. The sample mailbox is unchanged.
- Only the current page's message details are fetched. Pagination reads Gmail state and does not modify it or persist messages or page tokens.

## Invariants

1. Gmail remains the source of truth for email state
2. OAuth tokens must never be exposed to the frontend
3. Emails from different Gmail accounts must never be merged into the same thread
4. Every displayed email must preserve its source Gmail account
5. The application must not permanently store the full Gmail mailbox
6. Star and label changes must be synchronized with Gmail
