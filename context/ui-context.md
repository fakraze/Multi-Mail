# UI Context

## Theme

Light mode only. Use a clean Gmail-inspired interface with soft gray backgrounds, white content areas, compact spacing, and minimal visual decoration.

## Colors

Use CSS custom properties only. Avoid hardcoded colors in components.

| Role            | CSS Variable       | Value     |
| --------------- | ------------------ | --------- |
| Page background | `--bg-base`        | `#F6F8FC` |
| Surface         | `--bg-surface`     | `#FFFFFF` |
| Primary text    | `--text-primary`   | `#1F1F1F` |
| Muted text      | `--text-muted`     | `#5F6368` |
| Primary accent  | `--accent-primary` | `#0B57D0` |
| Border          | `--border-default` | `#DADCE0` |
| Error           | `--state-error`    | `#B3261E` |
| Success         | `--state-success`  | `#188038` |
| Search highlight | `--search-highlight` | `#FFF2A8` |

## Typography

| Role      | Font                               | Variable      |
| --------- | ---------------------------------- | ------------- |
| UI text   | Arial / Roboto / system sans-serif | `--font-sans` |
| Code/mono | system monospace                   | `--font-mono` |

## Border Radius

| Context           | Class        |
| ----------------- | ------------ |
| Inline / small UI | `rounded-md` |
| Cards / panels    | `rounded-xl` |
| Modals / overlays | `rounded-xl` |

## Component Library

Use reusable React components styled to match Gmail. Avoid components with heavy dashboard-style visuals.

## Layout Patterns

- The Multi Mail title in the upper-left sidebar is a keyboard-accessible home button. It returns the current sample or connected mail view to its Inbox, clearing an active search or opened message in the connected view.
- Top bar with a large rounded search field.
- Left sidebar for inbox, starred, labels, and connected accounts.
- Main area for compact email rows.
- Email rows show sender, subject, preview, source account, and time.
- Right-align source-account chips in a narrow column beside the timestamp, with both aligned across mail rows. The chip shows only the part of the account before `@`; its full address remains available as a tooltip. In the list, show only the local time for messages from today and only the local date for earlier messages.
- Use subtle hover and selected states instead of heavy cards.
- Keep the mail frame within the viewport. The toolbar, left navigation, and account area stay in place; only the message list or opened message content scrolls.
- While reloading connected mail, show loading feedback in the message list and keep the previously loaded sidebar labels and account controls visible.
- On the connected search result list, highlight matching visible query terms in sender, subject, and preview with the search highlight color. Quoted phrases remain whole; Gmail filter operators such as `after:` and `in:` are not highlight terms. Highlighting is visual only and does not alter the Gmail query.

## Icons

Use Lucide React. Stroke-based icons only. Use `16px` for inline actions and `20px` for toolbar buttons.
