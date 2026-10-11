# Progress Tracker

Update this file after every meaningful implementation change.

## Current Phase

- 08 Mail pagination complete

## Current Goal

- Choose the next feature unit from Next Up; multi-account aggregation remains a later phase.

## Completed

**01-design-system:** Built the Gmail-inspired light theme, design tokens, shadcn/ui components, and Lucide icons; frontend lint and build passed.

**02-main-page:** Built the sample mailbox with navigation, account controls, selection, and mail actions; Gmail-dependent controls initially showed placeholders. Frontend lint and build passed.

**03-login-page:** Added the Google connection page with Continue with Google and Back navigation to the originating mail view; frontend lint and build passed.

**04-google-oauth:** Added local Google OAuth start and callback routes with state validation, safe errors, and backend-only token handling. The live consent flow succeeded; backend tests, frontend lint, and build passed.

**04b-local-token-storage:** Saved the latest OAuth grant atomically in ignored `backend/oauth_tokens.json`, with controlled storage errors and no frontend token exposure. Live authorization and backend tests passed.

**05-gmail-access:** Added a backend-only Gmail profile check using the latest grant, in-memory token refresh, and controlled errors. Live account verification and backend tests passed.

**05b-live-inbox:** Connected the OAuth return page to the latest account's 20 newest INBOX messages and plain-text message reading while direct home visits keep the sample page. Preserved the compact mail layout, fixed scrolling and row alignment, and cleaned sender names; live checks, backend tests, frontend lint, and build passed.

**06-gmail-modify:** Added a backend-only command to star, unstar, add, or remove an allowed label on one Gmail message and verify the resulting state by reading it again. Live checks and backend tests passed; tokens and mail data stayed off the frontend and out of the database.

**06b-gmail-modify-ui:** Connected Starred, Important, and user-label filters and edits to Gmail on the live page. Added user-label creation and confirmed deletion from the sidebar, with account and INBOX checks and read-back after changes. The final UI excludes Categories and Purchases; the label picker offers only Important and user labels and shows `No labels applied.` when neither is present. Live API checks, 33 backend tests, frontend lint, and build passed.

**07-gmail-search:** Added single-account Gmail search through the existing backend mailbox API. The connected page displays up to 20 matching messages, supports Gmail query syntax, and highlights visible search terms in yellow in sender, subject, and preview. Search remains read-only and does not persist results. A live query, 35 backend tests, three highlight tests, frontend lint, and production build passed.

**08-mail-pagination:** The mailbox API loads at most 50 Gmail messages per page and returns Gmail's next-page token. The connected page shows previous/current/next controls, remembers tokens for visited pages, and resets to page 1 after search, folder, or refresh changes. Message rows and actions remain available. All 37 backend tests, frontend lint, and production build passed.

**Mail loading sidebar fix:** Refreshing, searching, or changing folders now keeps the last loaded mailbox metadata visible, so Important, user labels, and account controls remain in place while the message list loads. Frontend lint and production build passed.

**Home title navigation:** The Multi Mail title is a keyboard-accessible button in both sample and connected mail views. It returns to that view's Inbox, clears the active search or opened message as applicable, and preserves the connected Gmail view. Frontend lint and production build passed.

## In Progress

- None.

## Next Up

- database storage for persistent multiple-account tokens and faster mail access
- background process, update speed (save mail in DB but sync every user refresh and every miniute)
    First connection
        → Full sync
    Later syncs(user refresh and every 1 minute)
        → Incremental sync
    If incremental sync fails
        → Full sync fallback
- connect multiple accounts
- disconnect account
- account selection
- unified inbox
- multi account search
- format handling (image, html)
- thread mail(connect mail to previous mail and change user to all user in the mail)
## Open Questions

- None for the completed single-account Gmail search unit; its query and read-only behavior are documented in `architecture.md`.

## Architecture Decisions

- Frontend UI primitives live under `frontend/src/components/ui/` and use token-backed Tailwind classes with `frontend/src/lib/utils.ts` for class merging.
- The local OAuth route contract, latest-grant file storage, backend-only Gmail profile check, live single-account inbox, search, pagination and modification APIs, and backend-only Gmail modification command are documented in `architecture.md`. No database model was added.

## Session Notes

- The React app starts on the original sample mail page. Connect Gmail opens the login page, whose Back button returns to the originating sample or live mail view; Continue with Google navigates to the local FastAPI OAuth start route. On authorization success, the callback redirects home with `gmail=connected` and the frontend loads the latest grant's real Gmail inbox. Direct visits to `/` stay on the sample page even when a token file exists. The connected page filters INBOX mail by Starred or sidebar labels, supports star and displayed label changes in rows and opened messages, can create or delete Gmail user labels, searches the latest connected account, and paginates up to 50 messages at a time. While mail reloads, the sidebar retains Important, user labels, and account controls. The Multi Mail title returns the current mail view to Inbox. Multi-account storage and disconnect are not yet connected. Direct Uvicorn runs use `--no-access-log` so callback authorization codes are not written to request logs.
