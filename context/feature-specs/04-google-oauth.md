# Feature: Google OAuth Login

Read `AGENTS.md` before starting.

Implement the minimum Google OAuth 2.0 flow required to let a user sign in with Google and verify that the backend can obtain OAuth tokens.

## Tasks

- Add a backend route to start the Google OAuth flow.
- Redirect the user to Google's authorization page.
- Add a backend callback route to receive Google's OAuth response.
- Exchange the authorization code for OAuth tokens.
- Verify that the backend can successfully obtain an access token.
- Verify whether a refresh token is returned when applicable.
- Add a minimal frontend action or link that starts the OAuth flow.
- Use local development callback URLs only.
- Do not store OAuth tokens in the database yet.
- Do not implement Gmail inbox, search, star, label, or account management.
- Do not expose OAuth tokens to the frontend.
- Do not request or store the user's Gmail password.

## Check when done

- The user can start the Google login flow from the application.
- The Google authorization page opens successfully.
- The user can select a Google account and approve access.
- Google redirects successfully to the backend callback route.
- The backend receives the authorization code.
- The backend successfully exchanges the code for an access token.
- The OAuth token response can be verified through backend logs or a backend-only test output without exposing token values to the frontend.
- OAuth API failures are handled without crashing the backend.
- No OAuth tokens are stored in the database.
- The backend starts successfully.
- `npm run lint` passes.
- `npm run build` passes.