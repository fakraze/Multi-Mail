# Progress Tracker

Update this file after every meaningful implementation change.

## Current Phase

- 05b live single-account Gmail inbox and connected-page UI polish completed

## Current Goal

- Define and implement the next Gmail feature unit against its spec.

## Completed

**01-design-system:** Set up the light Gmail-inspired theme with design tokens, Tailwind, shadcn/ui base components, and Lucide icons. The components render, and `npm run lint` and `npm run build` passed.

**02-main-page:** Built the sample mail page with Connect Gmail, account Disconnect actions, Inbox, Starred, and expandable Labels navigation, account filtering, and mail selection, refresh, star, and label controls. Gmail-dependent actions show placeholder dialogs; `npm run lint` and `npm run build` passed.

**03-login-page:** Added a centered login page with a Multi Mail description and Continue with Google button. Connect Gmail opens it from the main page, and the button returns to the sample inbox with a sign-in placeholder notice; `npm run lint` and `npm run build` passed.

**04-google-oauth:** Added local Google authorization and callback routes, state validation, token exchange, backend-only token-presence logging, safe error pages, and a frontend Continue with Google action. The backend reads ignored `backend/.env` credentials with shell environment variables taking precedence. The user completed a live Google consent flow and confirmed `access_token=True refresh_token=True` in the backend log. The initial verification phase did not store tokens or accounts. Six backend tests, local backend startup checks, `npm run lint`, and `npm run build` passed.

**04b-local-token-storage:** The callback saves the latest successful OAuth grant to ignored `backend/oauth_tokens.json` using atomic replacement and restricted file mode where supported. Storage failures return a controlled error. A new live authorization created the local file; backend-only checks confirmed that both access and refresh tokens are present without printing their values. Eleven backend tests, frontend lint, and frontend build passed. Multi-account storage and Gmail API calls remain outside this step.

**05-gmail-access:** Added a backend-only check that loads the latest local grant, calls Gmail `users.getProfile`, refreshes an expired access token in memory when possible, and reports controlled errors. The existing `gmail.modify` scope authorizes this call, so no extra scope was needed. A live check retrieved the authorized Gmail account address. Fifteen backend tests and `npm run build` passed. No Gmail profile data or refreshed token was persisted, and the frontend received no token.

**05b-live-inbox:** OAuth success redirects to the configured frontend home URL with a non-secret connection marker. Direct home visits retain the original sample page; only the OAuth return URL loads the latest authorized Gmail account and up to 20 real INBOX messages through backend `GET /api/mailbox`, and opens a message as safe plain text through `GET /api/messages/{message_id}`. A live Gmail check loaded 20 messages and opened one body without printing its content. Eighteen backend tests, frontend lint, and frontend build passed. This remains a latest-grant, single-account flow; no Gmail content is persisted.

**05b connected-page parity:** Restored the sample page's sidebar, toolbar, selection controls, account row, and compact message actions on the live Gmail view. `GET /api/mailbox` now also returns read-only user and category/Important label names for the expandable sidebar. The connected account's live check returned 20 messages and six sidebar labels. Starred, search, label filtering/editing, star editing, and disconnect show an unavailable notice instead of changing Gmail. Eighteen backend tests, frontend lint, and frontend build passed.

**Login-page back navigation:** Added a visible Back button to the Google connection page. It returns to the sample or live mail view that opened Connect Gmail. Frontend lint and build passed.

**Mail layout scroll containment:** Fixed the mail frame to the viewport height and constrained overflow to the right-side message area. The sidebar navigation flexes within the available space so the account row stays anchored at the bottom; labels and toolbar remain in place while mail scrolls. Frontend lint and build passed.

**Sender display-name cleanup:** Live Gmail summaries now parse `From` headers into display names without surrounding quotes or email addresses, using the address local part when no name is provided. Nineteen backend tests and frontend build passed. A live check of 20 messages confirmed that returned sender labels contain no addresses or surrounding quotes.

**Mail-row alignment and date formatting:** Account chips and timestamps now use consistent columns in the live mail list, with a narrower-screen row layout when space is limited. Today's messages show local time only; earlier messages show local date only. Frontend lint and build passed.

**Mail-row account spacing:** Account chips now align to the right in a narrower column beside a tighter timestamp column, leaving more room for the subject. Frontend lint and build passed.

**Compact account-chip display:** Live mail-row chips now show only the account name before `@`, while retaining the full source address in the API data and chip tooltip. The account column is 100px wide, freeing more space for the subject. Frontend lint and build passed.

## In Progress

- None.

## Next Up

- Implement the next Gmail feature unit, then define multi-account aggregation and remaining API contracts.
- gmail modify (star, label)
- gmail search
- database for store multiple account token (token still persist after restart)
- connect multiple accounts
- disconnect account
- account selection
- unified inbox
- multi account search
- format handling (image, html)
- thread mail(connect mail to previous mail and change user to all user in the mail)
## Open Questions

- Define backend API contracts and label selection behavior before implementing live Gmail actions.

## Architecture Decisions

- Frontend UI primitives live under `frontend/src/components/ui/` and use token-backed Tailwind classes with `frontend/src/lib/utils.ts` for class merging.
- The local OAuth route contract, latest-grant file storage, backend-only Gmail profile check, and live single-account inbox API are documented in `architecture.md`. No database model was added.

## Session Notes

- The React app starts on the original sample mail page. Connect Gmail opens the login page, whose Back button returns to the originating sample or live mail view; Continue with Google navigates to the local FastAPI OAuth start route. On authorization success, the callback redirects home with `gmail=connected` and the frontend loads the latest grant's real Gmail inbox in the same layout as the sample page. Direct visits to `/` stay on the sample page even when a token file exists. A live backend check loaded 20 messages, six sidebar labels, and one message body. Multi-account storage, search, star, label edits, and disconnect are not yet connected. Direct Uvicorn runs use `--no-access-log` so callback authorization codes are not written to request logs.
