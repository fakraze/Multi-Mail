# Feature: Local OAuth Token Storage

Save the latest successful Google OAuth grant in a backend-only local file for later Gmail API verification.

## Tasks

- After a successful code exchange, write the access token and optional refresh token to `backend/oauth_tokens.json`.
- Replace the previous file on each successful authorization; do not infer or preserve an earlier account's refresh token when Google omits one.
- Ignore the token file in Git and use restrictive file permissions where supported.
- Keep token values out of frontend responses and logs.
- Handle local write failures without reporting OAuth success or crashing the backend.
- Do not call Gmail APIs, store tokens in SQLite, or implement multi-account management in this step.

## Check when done

- A mocked successful callback saves token values to the local file.
- A later grant replaces the previous values.
- A failed exchange leaves the existing file untouched.
- A write failure gives a controlled error page with no token values.
- Relevant backend tests pass.
