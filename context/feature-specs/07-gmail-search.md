# Feature: Gmail Search

Read `AGENTS.md` before starting.

Implement Gmail search for a single connected Gmail account using the existing Gmail API integration.

## Tasks

- Use the existing Gmail OAuth credentials and Gmail API integration.
- Add a single search input similar to Gmail's search bar.
- Send the user's search text directly to the Gmail API as the search query.
- Retrieve matching messages from Gmail.
- Return basic message information needed by the existing mail list UI.
- Keep all Gmail API calls on the backend.
- Use `backend/oauth_tokens.json` as the local test credential source.
- Do not add separate search fields for sender, recipient, subject, date, or labels.
- Do not implement multi-account search yet.
- Do not store search results in the database.
- Do not modify Gmail message state during search.
- Do not expose OAuth tokens to the frontend or logs.

## Check when done

- A single Gmail-like search box is available.
- Entering a query and submitting it searches the connected Gmail account.
- Matching messages are shown in the existing mail list.
- Visible matches for search words or quoted phrases are highlighted in yellow in each result's sender, subject, and preview. Gmail filter syntax is not highlighted as a word.
- Gmail search syntax entered directly in the search box is passed through correctly.
- Search does not modify Gmail mailbox state.
- Search operates on only one Gmail account.
- No search results are persisted in the database.
- OAuth tokens are not exposed to the frontend or logs.
- Gmail API errors are handled without crashing the application.
