# Feature: Background Mail Sync

Read `AGENTS.md` before starting.

Keep cached mail data synchronized with Gmail while preserving the existing UI during refresh.

## Tasks

- Use the database as the local mail cache.

- On first account connection:
  - Perform a full Gmail sync.
  - Store the mail data in the database.
  - Save the latest Gmail `historyId`.

- For later syncs triggered by:
  - user refresh
  - automatic sync every 1 minute

  perform an incremental Gmail sync using the saved `historyId`.

- Reset the 1-minute automatic sync timer after a user-triggered refresh.

- If incremental sync cannot continue, fall back to a full Gmail sync.

- Run mail synchronization without clearing the currently displayed mail list.
- Keep the existing mail page visible while synchronization is in progress.
- For user-triggered refresh:
  - show a visible `Loading` indicator while synchronization is running
  - hide the `Loading` indicator when synchronization finishes or fails
- For automatic sync:
  - do not show the `Loading` indicator
  - keep the synchronization silent in the background
- Do not replace the existing mail list with an empty loading screen.

- After synchronization finishes successfully:
  - update the database
  - reload the mail data from the database
  - update the displayed mail list

- If synchronization fails:
  - keep the existing cached mail visible
  - report the error without clearing the current mail list

## Check when done

- First connection performs a full Gmail sync.
- Later refreshes use incremental sync.
- Automatic synchronization runs every 1 minute.
- A user-triggered refresh resets the automatic sync timer.
- Incremental sync falls back to full sync when necessary.
- Existing mail remains visible while synchronization is running.
- User-triggered refresh shows a `Loading` indicator.
- Automatic sync does not show a `Loading` indicator.
- The UI does not temporarily show an empty mail list during synchronization.
- After a successful sync, the displayed mail updates to the latest database state.
- If sync fails, the previously displayed cached mail remains visible.