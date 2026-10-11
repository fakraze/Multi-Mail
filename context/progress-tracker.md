# Progress Tracker

Update this file after every meaningful implementation change.

## Current Phase

- 06g Labels and Important only complete

## Current Goal

- Implement the next Gmail feature unit and define multi-account aggregation.

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

**06-gmail-modify:** Added a backend-only command for explicit star, unstar, add-label, and remove-label actions using the latest local OAuth grant. It validates the target message, restricts label changes to user labels or Important, and reads the same message back after each modification. A live check successfully performed all four actions on one Gmail message and restored its initial labels (`CATEGORY_FORUMS`, `INBOX`). All 23 backend tests, frontend build, and `git diff --check` passed. No Gmail data or credentials were written to the database or sent to the frontend.

**06b-gmail-modify-ui:** Connected the live page's star buttons, label picker, Starred navigation, and sidebar label filters to Gmail. The backend checks account and INBOX scope, modifies only the requested label, and returns the same message's verified Gmail state; the UI updates its list and opened message from that response. Category labels are filter-only. Live HTTP checks confirmed star and Important changes appear in their filtered views and restored the message's original state. All 27 backend tests, frontend build and lint, CORS preflight, and `git diff --check` passed.

**06c-gmail-labels:** Enabled editing for the displayed Gmail category labels and added a plus button beside live Labels to create a Gmail user label. The backend verifies the new label through Gmail read-back, and the frontend adds it to the sidebar and message picker. A live test created a temporary label, applied it to a message, filtered by it, and removed it from the message. Thirty backend tests and frontend build/lint passed.

**06d-gmail-label-delete:** Added a delete button only for Gmail user labels, with a confirmation dialog explaining that Gmail removes the label from associated messages. The backend checks account and user-label type, calls Gmail delete, and confirms the ID is absent. A live HTTP check deleted the previously created empty temporary label and verified it was gone. All 33 backend tests, frontend build and lint passed.

**06e-gmail-categories:** Separated the live sidebar into Categories and user Labels; Important remains a separate filter. Localized the five Gmail category names, including Primary as 主要. Added 購物交易 as a read-only virtual view using Gmail `category:purchases` search within INBOX; it cannot be applied to a message or deleted as a label. Added `kind` to mailbox label entries and the create-label response so the frontend distinguishes user, system, and view entries. Live HTTP checks returned 20 Purchases messages and the Chinese category names; the local frontend returned HTTP 200. All 33 backend tests, frontend build and lint, and `git diff --check` passed.

**06f-english-category-sidebar:** Restored English display names for Primary, Social, Promotions, Updates, Forums, and Purchases. The connected Categories sidebar excludes Primary and displays the other four Gmail categories plus Purchases, for five entries. Primary remains available as a Gmail system classification through the mailbox API and message label picker. A live API check found all five English names and 20 Purchases messages; all 33 backend tests, frontend build, and lint passed.

**06g-labels-only:** Removed the connected Categories sidebar, the Purchases view, and all Gmail category entries from the mailbox label API and message label dialog. Only user labels and Important are selectable or editable; category filter and modify requests are rejected. The dialog says "No labels applied." when a message has neither a user label nor Important, including messages with only Primary. A live mailbox API check returned Important and a user label with zero category entries and 20 messages. All 33 backend tests, frontend build, and lint passed.

**06b consolidated spec:** Added `context/feature-specs/06b-gmail-modify-ui.md` to describe the final connected-page behavior across the 06b through 06g updates: star and label edits, Gmail-backed filters, user label creation and deletion, Important, and exclusion of Categories. The separate 06 backend modification verification remains in `06-gmail-modify.md`.

## In Progress

- None.

## Next Up

- Implement the next Gmail feature unit, then define multi-account aggregation and remaining API contracts.
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

- None for the current single-account star and label unit; its route and label selection rules are documented in `architecture.md`.

## Architecture Decisions

- Frontend UI primitives live under `frontend/src/components/ui/` and use token-backed Tailwind classes with `frontend/src/lib/utils.ts` for class merging.
- The local OAuth route contract, latest-grant file storage, backend-only Gmail profile check, live single-account inbox and modification APIs, and backend-only Gmail modification command are documented in `architecture.md`. No database model was added.

## Session Notes

- The React app starts on the original sample mail page. Connect Gmail opens the login page, whose Back button returns to the originating sample or live mail view; Continue with Google navigates to the local FastAPI OAuth start route. On authorization success, the callback redirects home with `gmail=connected` and the frontend loads the latest grant's real Gmail inbox. Direct visits to `/` stay on the sample page even when a token file exists. The connected page filters INBOX mail by Starred or sidebar labels, supports star and displayed label changes in rows and opened messages, and can create or delete Gmail user labels from the sidebar. A live HTTP check verified the create/apply/filter/remove/delete flow and left no temporary test label. Multi-account storage, search, and disconnect are not yet connected. Direct Uvicorn runs use `--no-access-log` so callback authorization codes are not written to request logs.
