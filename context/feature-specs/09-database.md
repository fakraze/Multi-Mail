# Feature: Database Persistence

Read `AGENTS.md` before starting.

Set up local database persistence for one connected Gmail account, OAuth credentials, and cached mail data.

## Tasks

- Configure SQLite as the local database.
- Configure SQLAlchemy for database access.

- Create a database model for one connected Gmail account.
- Store account information required to identify the connected Gmail account.
- Store OAuth credentials required for continued Gmail API access.

- Create a database model for cached Gmail messages.
- Store the mail information required by the existing mail list UI, including:
  - Gmail message ID
  - Gmail thread ID
  - sender
  - subject
  - snippet
  - timestamp
  - star state
  - labels

- Associate cached messages with the connected Gmail account.

- When mail data is requested:
  - If cached mail data exists in the database, read and return the cached data.
  - If cached mail data does not exist, retrieve it from the Gmail API, store it in the database, and return it.

- Gmail remains the source of truth.
- The database acts as a local read cache.
- Ensure account, token, and cached mail data persist after backend restart.
- Keep database access inside the backend.
- Do not expose OAuth tokens to the frontend or logs.
- Do not implement support for multiple Gmail accounts yet.
- Do not implement Gmail full sync, incremental sync, automatic refresh, or scheduled synchronization yet.
- Do not modify Gmail data as part of database operations.

## Check when done

- SQLite database initializes successfully.
- SQLAlchemy can read and write database records.
- One Gmail account can be stored and retrieved.
- OAuth credentials can be stored and retrieved by the backend.
- Cached Gmail messages can be stored and retrieved.
- Cached messages remain associated with the connected Gmail account.
- When cached mail exists, mail is returned from the database without calling Gmail.
- When cached mail does not exist, Gmail is called and the returned mail is stored in the database.
- Account, token, and mail data remain available after backend restart.
- OAuth tokens are not exposed to the frontend or logs.
- No Gmail synchronization logic is implemented.