# Progress Tracker

Update this file after every meaningful implementation change.

## Current Phase

- 12 Bulk Mail Actions completed; ready for the next feature.

## Current Goal

- Select the next feature unit from the remaining roadmap.

## Completed

**01-design-system:** Built the Gmail-inspired light theme, design tokens, shadcn/ui components, and Lucide icons; frontend lint and build passed.

**02-main-page:** Built the sample mailbox with navigation, account controls, selection, and mail actions; Gmail-dependent controls initially showed placeholders. The Multi Mail title is a keyboard-accessible button that returns both sample and connected views to Inbox, clearing an active search or opened message as applicable. Frontend lint and build passed.

**03-login-page:** Added the Google connection page with Continue with Google and Back navigation to the originating mail view; frontend lint and build passed.

**04-google-oauth:** Added local Google OAuth start and callback routes with state validation, safe errors, and backend-only token handling. The live consent flow succeeded; backend tests, frontend lint, and build passed.

**04b-local-token-storage:** Saved the latest OAuth grant atomically in ignored `backend/oauth_tokens.json`, with controlled storage errors and no frontend token exposure. Live authorization and backend tests passed.

**05-gmail-access-read:** Added a backend-only Gmail profile check using the latest grant, in-memory token refresh, and controlled errors. Live account verification and backend tests passed.

**05b-live-inbox:** Connected the OAuth return page to the latest account's 20 newest INBOX messages and plain-text message reading while direct home visits keep the sample page. Preserved the compact mail layout, fixed scrolling and row alignment, and cleaned sender names; live checks, backend tests, frontend lint, and build passed.

**06-gmail-modify:** Added a backend-only command to star, unstar, add, or remove an allowed label on one Gmail message and verify the resulting state by reading it again. Live checks and backend tests passed; tokens and mail data stayed off the frontend and out of the database.

**06b-gmail-modify-ui:** Connected Starred, Important, and user-label filters and edits to Gmail on the live page. Added user-label creation and confirmed deletion from the sidebar, with account and INBOX checks and read-back after changes. The final UI excludes Categories and Purchases; the label picker offers only Important and user labels and shows `No labels applied.` when neither is present. A later fix made Important visible immediately and ensured fresh and cached mailbox responses include its metadata, even when Gmail omits it from the label list. Star and unstar use `PATCH /api/messages/{message_id}/labels` with `label_id=STARRED` and `present=true` or `false`. Live API checks, 39 backend tests, frontend lint, and build passed.

**07-gmail-search:** Added single-account Gmail search through the existing backend mailbox API. The connected page displays up to 20 matching messages, supports Gmail query syntax, and highlights visible search terms in yellow in sender, subject, and preview. Search remains read-only and does not persist results. A live query, 35 backend tests, three highlight tests, frontend lint, and production build passed.

**08-mail-pagination:** The mailbox API loads at most 50 Gmail messages per page and returns Gmail's next-page token. The connected page shows previous/current/next controls, remembers tokens for visited pages, and resets to page 1 after search, folder, or refresh changes. Message rows and actions remain available. While mail reloads, Important, user labels, and account controls remain visible. All 37 backend tests, frontend lint, and production build passed.

**09-database:** Added ignored SQLite storage through SQLAlchemy for one connected Gmail account, backend-only OAuth credentials, message summaries, and mailbox pages. Requested pages are read from SQLite when present and fetched from Gmail and cached when absent. Confirmed Gmail label and star actions invalidate cached pages; there is no automatic sync. A legacy token file is migrated on first access. Persistence across a new database connection and cache hit/miss behavior are covered by tests. All 38 backend tests and the frontend production build passed.

**10-background-sync:** Added a SQLite Gmail history cursor, first-connection Inbox sync, and a sync endpoint that uses paginated Gmail history to refresh only requested mailbox pages when needed. Manual refresh and the one-minute timer keep existing mail visible; the toolbar shows loading feedback for manual refresh. Folder, search, pagination, and cached-page reloads also retain the prior rows until the next view succeeds. All 46 backend tests, frontend lint, and production build passed.

**11-background-modify:** Added optimistic star, unstar, add-label, and remove-label actions. Controls stay interactive and fully opaque while changes run in the background. Consecutive changes to one message appear immediately and reach Gmail in click order; different messages can update concurrently. On failure the UI reconciles with Gmail or restores the last confirmed state, then reapplies queued changes. The backend stores Gmail-confirmed labels and star state in the cached message row while invalidating pages in one transaction; failed Gmail requests leave SQLite unchanged. All 49 backend tests, frontend lint, and production build passed. Pushed to `origin/main` in commit `3ae1ff6`.

**12-multi-modify:** Added current-page bulk controls for explicit star, unstar, add-label, and remove-label actions. Every selected message changes on screen immediately; the Gmail-confirmed requests run in the background through the existing per-message queues, with controls still interactive. Each successful request updates its cached summary. The selection and selected rows remain visible after the action, including when a row no longer matches the current filter. Search results outside INBOX disable bulk modifications in keeping with the existing API restriction. Frontend lint and production build passed after the background update; all 49 backend tests passed for the unchanged modification route. Live Gmail verification was not run.

**Current-folder sidebar refresh:** Clicking the currently active Inbox, Starred, Important, or user label now runs the same manual Gmail sync as toolbar Refresh, while keeping the current mail list visible during loading. Frontend lint and production build passed.

## In Progress

- None.

## Next Up

- DB for multiple account
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
- The local OAuth route contract, backend-only Gmail profile check, live single-account inbox, search, pagination and modification APIs, and backend-only Gmail modification command are documented in `architecture.md`. Feature 09 replaces latest-grant file storage with an SQLite account record and a backend-only mailbox-page cache.

## Session Notes

- The root README documents the current version's local setup, frontend/backend data flow, HTTP API, SQLite tables, cache and sync behavior, and verification commands. The backend README describes first sync and history-based refresh.
- The React app starts on the original sample mail page. Connect Gmail opens the login page, whose Back button returns to the originating sample or live mail view; Continue with Google navigates to the local FastAPI OAuth start route. On authorization success, the callback redirects home with `gmail=connected` and the frontend loads the latest grant's real Gmail inbox. Direct visits to `/` stay on the sample page even when a database grant exists. The connected page filters INBOX mail by Starred or sidebar labels, supports star and displayed label changes in rows and opened messages, can create or delete Gmail user labels, searches the latest connected account, and paginates up to 50 messages at a time. Requested pages are cached in SQLite and remain unchanged until invalidated by a Gmail action or later synchronization work. While mail reloads, the sidebar retains Important, user labels, and account controls. The Multi Mail title returns the current mail view to Inbox. Multi-account storage and disconnect are not yet connected. Direct Uvicorn runs use `--no-access-log` so callback authorization codes are not written to request logs.
