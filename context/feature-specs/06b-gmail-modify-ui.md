# Feature: Gmail modification on the connected mail page

Read `AGENTS.md` before starting. Apply the existing Gmail modification capability to the live single-account page opened through `?gmail=connected`.

## Scope

- Keep the sample mailbox shown at `/` separate from the connected Gmail page. Use the latest authorized Gmail account for the connected page and keep Gmail API calls and OAuth credentials on the backend.
- The connected page shows Inbox, Starred, Important, and an expandable Labels group containing Gmail user-created labels. Important is a separate system marker. The Labels group has a plus button for creating a user label and a delete button beside each deletable user label.
- Do not show a Categories group or a Purchases view. Do not expose Primary or any other `CATEGORY_*` label in the sidebar or message label picker. Gmail may still report category IDs in a message's raw `label_ids`; they are not treated as app labels.
- `GET /api/mailbox` returns the account, up to 20 newest INBOX messages, and selectable labels. The label list contains only Gmail user labels and Important. Each label has `id`, `name`, `kind` (`user` or `system`), `modifiable`, and `deletable`. Only user labels are deletable.
- `GET /api/mailbox?label_id=...` filters INBOX messages by `STARRED`, `IMPORTANT`, or one of the account's user label IDs. Reject unknown IDs, category IDs, and `PURCHASES`. Sidebar selection fetches the corresponding Gmail-filtered mailbox.
- The star button beside each mail row and in an opened message adds or removes `STARRED`. The label button opens a dialog listing only Important and the account's user labels as checkboxes. A checkbox adds or removes that label on the selected INBOX message. When none of these labels is applied, show `No labels applied.` even if Gmail reports Primary or another category.
- `PATCH /api/messages/{message_id}/labels` accepts `{account, label_id, present}`. It permits `STARRED`, `IMPORTANT`, and Gmail user label IDs only. Verify the connected account and INBOX membership, change only the requested label, read the same Gmail message again, and return its confirmed `id`, `account`, `label_ids`, and `starred` state. Reject category IDs and unrelated system labels. Update the mail row, opened message, and label dialog from the confirmed response; remove a row from a selected filter when it no longer matches.
- `POST /api/labels` accepts `{account, name}`. Validate the name, reject a duplicate for that account, create a Gmail user label, read Gmail's label list again to confirm its ID and name, and return it as a modifiable, deletable `kind: user` label. Add it to the sidebar and label dialog without reauthorizing Gmail.
- `DELETE /api/labels/{label_id}?account=...` deletes only a Gmail user label after a confirmation dialog explains that the label will be removed from associated messages without deleting those messages. Verify the account and label type, delete it in Gmail, and confirm its ID is absent. Remove it from local sidebar and message state; return to Inbox if its filter was active. Never show a delete button for Important.
- Show controlled errors for rejected requests or Gmail failures. Never expose credentials or email content in errors, and do not persist Gmail messages, label state, or refreshed tokens in the application database.

## Check when done

- Star and unstar work from a mail row and opened message, and the Starred filter reflects the confirmed Gmail state.
- Important and any user-created label can be added to or removed from an INBOX message; their filters reflect Gmail state.
- The label picker has no Primary or category option. A message with only a Gmail category shows `No labels applied.` while Important and user labels remain available to add.
- A user can create a label from the left sidebar, apply it to a message, filter by it, remove it from the message, and delete the label. Gmail confirms each change.
- Only user labels have delete controls; deleting a label leaves its messages intact.
- Categories and Purchases are absent from navigation and label editing, and their IDs are rejected by mailbox filtering and message modification.
- The connected page handles account changes, non-INBOX messages, invalid IDs, and Gmail API errors without changing another account's message or exposing tokens.
- Backend tests, frontend lint, and frontend build pass.
