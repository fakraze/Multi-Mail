# Feature: Mail Pagination

Read `AGENTS.md` before starting.

Allow the user to browse all available Gmail messages using paginated mail loading.

## Tasks

- Display up to 50 emails per page.
- Add pagination controls to the mail list:
  - `<` goes to the previous page.
  - The current page number is displayed in the middle.
  - `>` goes to the next page.
- The first page is page `1`.
- Disable the previous-page action when already on page `1`.
- Disable the next-page action when there are no more emails.
- Load the corresponding Gmail messages when the user changes pages.
- Track Gmail page tokens so the user can navigate both forward and backward between previously loaded pages.
- Preserve the existing mail row UI and behavior.
- Keep Gmail API calls on the backend.
- Do not load all Gmail messages into the frontend at once.
- Do not modify Gmail message state as part of pagination.

## Check when done

- Each page displays at most 50 emails.
- The initial mail list opens on page `1`.
- The pagination control displays the current page as `< 1 >`.
- Clicking `>` loads the next 50 emails.
- Clicking `<` returns to the previous page.
- The current page number updates correctly.
- The previous-page action is disabled on page `1`.
- The user can continue navigating until all available emails have been reached.
- The next-page action is disabled when no more emails are available.
- Existing mail row actions continue to work.
- Gmail API errors are handled without crashing the application.
- `npm run lint` passes.
- `npm run build` passes.