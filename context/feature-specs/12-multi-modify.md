# Feature: Bulk Mail Actions

Read `AGENTS.md` before starting.

Allow the user to apply star and label actions to multiple selected emails at once.

## Tasks

- Allow the user to select multiple emails using the existing email checkboxes.
- Keep the existing select-all checkbox behavior for selecting the current page.

- When one or more emails are selected:
  - show bulk action controls in the top-right area of the mail section
  - show a star action
  - show a label action

- The star action must support:
  - star all selected emails
  - unstar all selected emails

- The label action must support:
  - add a label to all selected emails
  - remove a label from all selected emails

- Apply the requested action only to the selected emails.
- Keep all Gmail modification requests on the backend.
- Update the local database after Gmail modification succeeds.
- Update the displayed mail state after the operation completes.
- Preserve unselected emails without modification.
- Keep the current selection after the operation.
- Do not implement archive, delete, mark read/unread, or other bulk actions in this feature.

## Check when done

- Multiple emails can be selected at the same time.
- The select-all checkbox selects all emails on the current page.
- When emails are selected, star and label bulk actions appear in the top-right area of the mail section.
- Selected emails can be starred together.
- Selected emails can be unstarred together.
- A label can be added to all selected emails.
- A label can be removed from all selected emails.
- Only selected emails are modified.
- Gmail and the local database remain consistent after the operation.
- The displayed mail state updates after the operation.
- The current selection remains after the operation.
- `npm run lint` passes.
- `npm run build` passes.