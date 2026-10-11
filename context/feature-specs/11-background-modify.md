# Feature: Optimistic Mail Actions

Read `AGENTS.md` before starting.

Update existing single-mail star and label actions to use optimistic UI updates.

## Tasks

- Apply star and label changes to the UI immediately after the user performs the action.
- Do not wait for the Gmail API response before updating the displayed mail state.
- Send the corresponding Gmail modification request in the background.
- Update the local database after the Gmail modification succeeds.
- If the Gmail modification fails:
  - restore the previous UI state
  - restore or preserve the previous database state
  - show an error indication to the user
- Prevent failed background updates from leaving the UI and Gmail state inconsistent.
- Apply this behavior to:
  - star
  - unstar
  - add label
  - remove label
- Keep Gmail as the source of truth.
- Do not implement bulk mail actions in this feature.

## Check when done

- Star/unstar updates appear immediately in the UI.
- Label/unlabel updates appear immediately in the UI.
- Gmail modification runs in the background.
- Successful Gmail updates remain visible.
- The local database is updated after a successful Gmail modification.
- Failed Gmail updates automatically roll back to the previous UI state.
- Failed updates do not leave incorrect state in the local database.
- Existing mail remains visible during the background operation.
- Gmail API errors are handled without crashing the application.
- `npm run lint` passes.
- `npm run build` passes.