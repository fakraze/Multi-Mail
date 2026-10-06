# Feature: Gmail Read-Only Access

Read `AGENTS.md` before starting.

Verify that the backend can use Google OAuth credentials to read Gmail data without modifying mailbox state.

## Tasks

- Enable the Gmail API for the Google Cloud project.
- Request the read-only Gmail OAuth scope required for this feature.
- Use the OAuth credentials obtained by the backend.
- Use `backend/oauth_tokens.json` as the local test credential source.
- Retrieve the authenticated Gmail profile.
- Retrieve a small list of Gmail messages.
- Retrieve metadata for at least one message.
- Keep all Gmail API calls on the backend.
- Do not modify any Gmail data.
- Do not store Gmail data or OAuth tokens in the database yet.
- Do not implement inbox aggregation, search, star, label, archive, delete, or read/unread modification.
- Do not expose raw OAuth tokens to the frontend or logs.

## Check when done

- Google OAuth authorization succeeds with read-only Gmail access.
- The backend can successfully retrieve the Gmail profile.
- The backend can successfully list Gmail messages.
- The backend can successfully retrieve metadata for at least one message.
- No Gmail mailbox state is modified.
- OAuth tokens are not exposed to the frontend or logs.
- No Gmail data or OAuth tokens are persisted in the database.
- Gmail API errors are handled without crashing the backend.