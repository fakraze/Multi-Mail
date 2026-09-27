# Multi Mail

## Overview

Multi mail is a interface that user can check and manage their mail from multiple Gmail at a unified inbox.

## Goals

1. Allow users to connect and disconnect multiple Gmail accounts.
2. Allow users to view emails from all connected accounts in a unified inbox, ordered chronologically.
3. Clearly indicate which Gmail account each displayed email belongs to.
4. Allow users to search emails across multiple connected accounts at the same time.
5. Allow users to select which connected accounts are active, so that only emails from the selected accounts are displayed and searched.
6. Allow users to star and unstar emails, with changes synchronized to Gmail.
7. Allow users to add and remove Gmail labels from emails, with changes synchronized to Gmail.

## Core User Flow

1. User connects one or more Gmail accounts.
2. User selects which connected accounts are active.
3. User views emails from the selected accounts in a unified inbox.
4. User searches emails across the selected accounts.
5. User opens an email to read its content and identify its source account.
6. User stars or unstars emails when needed.
7. User adds or removes Gmail labels from emails when needed.
8. Changes are synchronized with the corresponding Gmail account.

## Features

### Account Management

- Connect multiple Gmail accounts using Google OAuth.
- Disconnect previously connected Gmail accounts.
- Display all currently connected Gmail accounts.
- Select which connected accounts are active.

### Unified Inbox

- Display emails from all selected Gmail accounts in a single inbox.
- Sort emails chronologically.
- Show the source Gmail account for each email.
- Open and read email content.

### Cross-Account Search

- Search emails across multiple selected Gmail accounts at the same time.
- Merge search results from different accounts into a single result list.
- Show the source Gmail account for each search result.

### Email Actions

- Star and unstar emails.
- Synchronize star/unstar changes with Gmail.
- Add Gmail labels to emails.
- Remove Gmail labels from emails.
- Synchronize label changes with Gmail.

## Scope

### In Scope

- [What you are building]
- [What you are building]

### Out of Scope

- [What you are explicitly not building]
- [What you are explicitly not building]

## Scope

### In Scope

- Connect and disconnect multiple Gmail accounts using Google OAuth 2.0.
- Display emails from selected Gmail accounts in a unified inbox.
- Sort emails chronologically.
- Show the source Gmail account for each email.
- Search emails across multiple selected Gmail accounts.
- Open and read email content.
- Star and unstar emails with changes synchronized to Gmail.
- Add and remove Gmail labels with changes synchronized to Gmail.
- Store connected account information and OAuth credentials locally.
- Run the application locally during the MVP stage.

### Out of Scope

- Sending, replying to, or forwarding emails.
- Managing drafts, sent mail, spam, trash, or scheduled emails.
- Downloading or managing attachments.
- Email push notifications or real-time background synchronization.
- Permanently copying the full Gmail mailbox into the application's database.
- Advanced local full-text search or external search engines such as Elasticsearch.
- Multi-user accounts or application-level user authentication.
- Cloud deployment, production hosting, and CI/CD.
- Mobile applications.

## Success Criteria

1. A user can connect at least three Gmail accounts and view them as connected accounts in the application.
2. Emails from multiple selected Gmail accounts can be displayed together in a single inbox and ordered chronologically.
3. Each displayed email clearly shows which Gmail account it belongs to.
4. A user can search emails across multiple selected Gmail accounts and receive combined results.
5. A user can select or deselect connected Gmail accounts, and only emails from the selected accounts are displayed and searched.
6. A user can star or unstar an email, and the change is reflected in Gmail.
7. A user can add or remove a Gmail label, and the change is reflected in Gmail.
8. A user can disconnect a Gmail account, after which that account is no longer used for inbox, search, or email actions.
9. The MVP can be run and used locally without requiring cloud deployment.