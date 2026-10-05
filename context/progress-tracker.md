# Progress Tracker

Update this file after every meaningful implementation change.

## Current Phase

- 04-google-oauth completed; next feature not started

## Current Goal

- Define the next backend API contracts before connecting the sample mail page to Gmail.

## Completed

**01-design-system:** Set up the light Gmail-inspired theme with design tokens, Tailwind, shadcn/ui base components, and Lucide icons. The components render, and `npm run lint` and `npm run build` passed.

**02-main-page:** Built the sample mail page with Connect Gmail, account Disconnect actions, Inbox, Starred, and expandable Labels navigation, account filtering, and mail selection, refresh, star, and label controls. Gmail-dependent actions show placeholder dialogs; `npm run lint` and `npm run build` passed.

**03-login-page:** Added a centered login page with a Multi Mail description and Continue with Google button. Connect Gmail opens it from the main page, and the button returns to the sample inbox with a sign-in placeholder notice; `npm run lint` and `npm run build` passed.

**04-google-oauth:** Added local Google authorization and callback routes, state validation, token exchange, backend-only token-presence logging, safe error pages, and a frontend Continue with Google action. The backend reads ignored `backend/.env` credentials with shell environment variables taking precedence. The user completed a live Google consent flow and confirmed `access_token=True refresh_token=True` in the backend log. No tokens or accounts are stored. Six backend tests, local backend startup checks, `npm run lint`, and `npm run build` passed.

## In Progress

- None.

## Next Up

- Connect the main mail page to backend account, inbox, search, star, and label APIs when their contracts are specified and implemented.

## Open Questions

- Define backend API contracts and label selection behavior before implementing live Gmail actions.

## Architecture Decisions

- Frontend UI primitives live under `frontend/src/components/ui/` and use token-backed Tailwind classes with `frontend/src/lib/utils.ts` for class merging.
- The local OAuth route contract and temporary token handling are documented in `architecture.md`. No database model was added.

## Session Notes

- The React app starts on the main mail page. Connect Gmail opens the login page, and Continue with Google navigates to the local FastAPI OAuth start route. The user verified a live access token and refresh token in backend logs. Folder, label, and account filtering still run only against sample data; Gmail actions remain a frontend preview. The backend does not save connected accounts or tokens. Direct Uvicorn runs use `--no-access-log` so callback authorization codes are not written to request logs.
