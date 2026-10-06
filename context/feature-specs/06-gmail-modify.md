# Feature: Gmail Modify Access

Read `AGENTS.md` before starting.

Verify that the backend can use Google OAuth credentials to modify Gmail message state.

## Tasks

- Request the Gmail OAuth scope required to modify message state.
- Use the OAuth credentials obtained by the backend.
- Use `backend/oauth_tokens.json` as the local test credential source.
- Add support for starring a Gmail message.
- Add support for unstarring a Gmail message.
- Add support for adding a label to a Gmail message.
- Add support for removing a label from a Gmail message.
- Keep all Gmail API calls on the backend.
- Verify each modification by reading the message state again after the operation.
- Do not implement archive, delete, send, reply, forward, or read/unread modification.
- Do not store Gmail data or OAuth tokens in the database yet.
- Do not expose raw OAuth tokens to the frontend or logs.

## Check when done

- Google OAuth authorization succeeds with Gmail modify access.
- The backend can successfully star a message.
- The backend can successfully unstar a message.
- The backend can successfully add a label to a message.
- The backend can successfully remove a label from a message.
- Each modification is reflected in Gmail when the message is retrieved again.
- Operations only affect the intended Gmail message.
- OAuth tokens are not exposed to the frontend or logs.
- No Gmail data or OAuth tokens are persisted in the database.
- Gmail API errors are handled without crashing the backend.