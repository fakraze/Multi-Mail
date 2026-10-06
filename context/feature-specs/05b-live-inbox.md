# Feature: Return to live single-account inbox

After a successful Google authorization, return to the local frontend home page. Use the latest backend-only OAuth grant to show that Gmail account's real inbox.

## Scope

- The default frontend home page remains the original sample mailbox, even when an older local grant exists. It does not call the live mailbox API on initial entry.
- The callback redirects to the configured local frontend URL with a non-secret `gmail=connected` marker after saving the grant. The frontend switches to the live mailbox only for that return URL. Errors retain the safe backend error page.
- The frontend requests the mailbox through the backend. The backend loads the latest local grant, refreshes expired access in memory, and calls Gmail. No token is sent to the frontend.
- `GET /api/mailbox` returns the Gmail account address and the newest 20 INBOX messages with ID, sender display name, subject, snippet, timestamp, and starred state. The sender display name excludes surrounding quotes and the email address; if Gmail provides no display name, use the email address's local part. A message keeps its source account address. Empty inboxes return an empty list.
- `GET /api/messages/{message_id}` returns one INBOX message from the same account with plain text body for reading. Message IDs are validated; HTML is never rendered as executable markup.
- The connected home page shows loading, empty, and error states; refresh fetches Gmail again. A row opens the message content.
- The connected home page keeps the sample page's layout and controls: Connect Gmail, Inbox and Starred navigation, expandable Labels, account checkbox and Disconnect, select-all and per-message checkboxes, refresh, search field, star and label icons, and compact rows. The account address and messages come from Gmail. User-created Gmail labels and available category/Important labels are listed read-only in the sidebar with readable names. Selection and the single-account checkbox work locally. Search, Starred navigation, label filtering, star/label edits, and disconnect show a clear unavailable notice until their feature units are implemented; they do not silently change Gmail.
- The connected page keeps the left navigation and account area visible while the right-side message list or opened message scrolls. The browser page and left sidebar do not scroll with the messages.
- Account chips and timestamps line up in fixed, compact columns. Account chips show only the part before `@`, with the full source account retained in the API response and tooltip. List timestamps use the browser's local calendar day: time only for today, date only for yesterday or earlier.
- Only the latest local grant is supported. Multi-account storage, aggregation, search, stars, labels, and disconnect are separate feature units.
- No Gmail content is persisted locally. Existing OAuth credential storage remains backend-only.

## Check when done

- Opening the frontend home URL shows the sample mailbox. Google authorization returns directly to the frontend home page in live Gmail mode.
- The home page identifies the authorized Gmail account and displays its real INBOX messages.
- Opening a row displays the corresponding message content safely.
- Network and Gmail API failures show a controlled error without crashing the app or exposing tokens.
