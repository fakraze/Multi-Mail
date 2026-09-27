# Code Standards

## General

- Keep modules and components small and single-purpose.
- Prefer simple solutions over unnecessary abstraction.
- Fix root causes instead of adding workarounds.
- Avoid unrelated changes in the same implementation step.

## TypeScript

- Keep TypeScript strict mode enabled.
- Avoid `any`; use explicit types or `unknown`.
- Validate external data before using it.
- Keep shared types in dedicated type files.

## React + Vite

- Use functional components.
- Keep API logic out of UI components.
- Keep `App.tsx` small.
- Use `VITE_` only for non-secret frontend environment variables.
- Never expose secrets or OAuth tokens to the frontend.

## FastAPI

- Keep route handlers focused on request/response handling.
- Put Gmail and OAuth logic in service modules.
- Use Pydantic models for API schemas.
- Return consistent HTTP responses.

## Gmail

- Use Google OAuth 2.0 and Gmail API.
- Never store Gmail passwords.
- Keep OAuth tokens on the backend.
- Treat Gmail as the source of truth.
- Star and label changes must synchronize with Gmail.
- Always preserve the source Gmail account for each email.

## Data

- Use SQLite + SQLAlchemy for the MVP.
- Store account and application metadata in the database.
- Do not copy the entire Gmail mailbox into the database.
- Do not log tokens or sensitive email content.

## Security

- Never commit `.env`, tokens, or credentials.
- Treat email HTML as untrusted.
- Do not allow email content to execute arbitrary JavaScript.

## Testing

- Add or update tests when behavior changes.
- Mock Gmail API calls in unit tests.
- Add regression tests for bug fixes when practical.

## File Organization

- `frontend/src/components/` — reusable UI components
- `frontend/src/pages/` — page-level components
- `frontend/src/services/` — backend API calls
- `frontend/src/types/` — shared TypeScript types
- `backend/app/api/` — FastAPI routes
- `backend/app/services/` — Gmail/OAuth/business logic
- `backend/app/models/` — SQLAlchemy models
- `backend/app/schemas/` — Pydantic schemas