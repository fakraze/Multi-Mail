# Architecture Context

## Stack

| Layer             | Technology                | Role                           |
| ----------------- | ------------------------- | ------------------------------ |
| Frontend          | React + TypeScript + Vite | User interface                 |
| Backend           | FastAPI                   | API and business logic         |
| Auth              | Google OAuth 2.0          | Gmail account authorization    |
| Gmail Integration | Gmail API                 | Read and modify Gmail data     |
| ORM               | SQLAlchemy                | Database access                |
| Database          | SQLite                    | Local application data storage |

## System Boundaries

- `frontend/` — UI, account selection, inbox display, search, and user interactions
- `backend/app/api/` — FastAPI routes and request/response handling
- `backend/app/services/` — Gmail API, OAuth, and business logic
- `backend/app/models/` — SQLAlchemy database models
- `backend/app/schemas/` — Pydantic request and response models

## Storage Model

- **SQLite Database**: Connected Gmail accounts, OAuth credentials, and application metadata
- **Gmail**: Email content, threads, stars, labels, and mailbox state
- Full Gmail mailboxes are not permanently copied into the local database

## Auth and Access Model

- Gmail accounts are connected through Google OAuth 2.0
- Gmail passwords are never collected or stored
- OAuth credentials are stored and used only by the backend
- The frontend communicates with Gmail only through the backend
- Every Gmail operation must use the credentials of the corresponding connected account

## Invariants

1. Gmail remains the source of truth for email state
2. OAuth tokens must never be exposed to the frontend
3. Emails from different Gmail accounts must never be merged into the same thread
4. Every displayed email must preserve its source Gmail account
5. The application must not permanently store the full Gmail mailbox
6. Star and label changes must be synchronized with Gmail