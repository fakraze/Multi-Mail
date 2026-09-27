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

- Top bar with a large rounded search field.
- Left sidebar for inbox, starred, labels, and connected accounts.
- Main area for compact email rows.
- Email rows show sender, subject, preview, source account, and time.
- Use subtle hover and selected states instead of heavy cards.

## Icons

Use Lucide React. Stroke-based icons only. Use `16px` for inline actions and `20px` for toolbar buttons.