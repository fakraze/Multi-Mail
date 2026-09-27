# Feature: Design System

Read `AGENTS.md` before starting.

Set up the base UI system for the Gmail-like interface.

## Tasks

- Configure the global design tokens defined in `ui-context.md`.
- Install and configure `shadcn/ui`.
- Add the following base components:
  - Button
  - Input
  - Checkbox
  - Dialog
  - DropdownMenu
  - Tooltip
  - ScrollArea
  - Separator
- Install `lucide-react`.
- Do not modify generated `components/ui/*` files unless necessary.
- Ensure components follow the light Gmail-inspired theme.

## Check when done

- The app builds successfully.
- Base UI components can be imported and rendered.
- Components use the design tokens defined in `ui-context.md`.
- `npm run build` passes.
- All components import without errors