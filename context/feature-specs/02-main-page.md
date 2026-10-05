# Feature: Main Mail Page

Read `AGENTS.md` before starting.

Modify the current example page into the main mail page.

## Tasks

- Modify the current example page directly.
- Remove the `Compose` button from the top-left area.
- Replace it with a `Connect Gmail` button.
- In the middle-left navigation section:
  - Add a `Inbox` option.
  - Add a `Starred` option.
  - Add a `Labels` option.
  - The `Labels` option can be expanded and collapsed.
  - When expanded, show the available labels.
  - Selecting `Inbox`, `Starred`, or a label changes the mails shown in the main mail section.
- In the lower-left account section:
  - Keep the email account display.
  - Add a `Disconnect` action on the right side of each email account.
- In the main mail section toolbar:
  - Add a select-all checkbox.
  - Add a refresh button.
- For each email row:
  - Add a checkbox on the left.
  - Add a star indicator/action next to the checkbox.
  - Add a label indicator/action next to the star.


## Check when done

- The `Compose` button is removed.
- A `Connect Gmail` button is shown in the top-left area.
- Each email account in the lower-left section has a `Disconnect` action on its right.
- The main mail toolbar has:
  - a select-all checkbox
  - a refresh button
- Each email row has:
  - a checkbox
  - a star indicator/action
  - a label indicator/action
- `npm run build` passes.