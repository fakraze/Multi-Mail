# Progress Tracker

Update this file after every meaningful implementation change.

## Current Phase

- Main mail page frontend

## Current Goal

- Build the main mail page layout described in `feature-specs/02-main-page.md`.

## Completed

- Replaced the Vite starter React content with a single centered `Multi Mail` page.
- Simplified frontend styles to use the documented light theme CSS variables.
- Removed unused Vite starter image and SVG assets, including the default favicon reference.
- Initialized project Git tracking setup with ignore rules for `tmp/` and `note.txt`.
- Added workspace VS Code settings so the hidden `.git` folder can be shown in Explorer.
- Installed Tailwind, Radix UI primitives, `lucide-react`, and shadcn/ui helper dependencies for the frontend.
- Added shadcn/ui configuration, path aliases, global design tokens, and the base UI components: Button, Input, Checkbox, Dialog, DropdownMenu, Tooltip, ScrollArea, and Separator.
- Updated the React preview screen to render the base UI components against the Gmail-inspired theme.
- Verified the design system setup with `npm run lint` and `npm run build`.
- Replaced the design-system preview with the main mail page. The sidebar now shows Connect Gmail and a Disconnect action for each sample account.
- Added select-all and refresh controls to the mail toolbar, plus selection, star, and label controls to each sample email row.
- Selection works within the sample list. Gmail account, refresh, star, and label controls show an explanatory dialog until backend integration exists, so the preview does not imply Gmail was changed.
- Verified the main mail page, including the navigation update, with `npm run lint` and `npm run build`.
- Added Inbox and Starred navigation plus an expandable Labels list. Navigation filters the sample mail, and account checkboxes now filter the same sample list.
- Added sample star and label metadata so Starred and label views have distinct results. Select-all now applies to visible mail and shows a partial-selection state.

## In Progress

- None.

## Next Up

- Connect the main mail page to backend account, inbox, search, star, and label APIs when their contracts are specified and implemented.

## Open Questions

- Define backend API contracts and label selection behavior before implementing live Gmail actions.

## Architecture Decisions

- Frontend UI primitives live under `frontend/src/components/ui/` and use token-backed Tailwind classes with `frontend/src/lib/utils.ts` for class merging.
- No backend architecture or data model changes.

## Session Notes

- The React app renders the main mail page using sample accounts and messages. Folder, label, and account filtering runs only against sample data. Gmail actions remain a frontend preview because this repository has no backend yet.
