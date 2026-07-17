# TH-0075 — System Settings Appearance

Status: IN PROGRESS

Last updated: 2026-07-17

## Goal

Add a typed site-appearance section to `/settings` that lets one club configure safe light and dark visual themes while each browser chooses `system`, `light`, or `dark` display mode independently.

## Product decisions

- organization appearance is global for the installation;
- each future user chooses only the display mode; before identity exists this preference is stored in `localStorage`;
- arbitrary CSS is prohibited;
- customization uses typed design tokens with backend validation;
- both light and dark schemes are configurable;
- invalid low-contrast schemes are rejected with an explanation;
- changes apply without an application restart;
- saving is section-specific and protected by optimistic versioning;
- the first preview is isolated inside the settings page rather than applying an unsaved draft to the whole application;
- reset, cancel, copy, JSON import, and JSON export are included;
- theme JSON contains no secrets and is distinct from the future encrypted full-system configuration archive.

## Scope

### Backend

- add singleton `appearance_settings` persistence with its own version and timestamps;
- store typed global controls for font, density, radius, button/card styles, and shadows;
- store complete typed light and dark color-token sets;
- provide safe built-in presets and defaults;
- validate hex colors and WCAG-style contrast for text/background surfaces;
- reject stale writes with HTTP 409 and serialize concurrent writes with a row lock;
- append safe `appearance` history records and retain the latest 200 settings-history rows;
- add one additive Alembic migration and keep one migration head.

### Frontend

- replace the planned `Оформление` placeholder with a working responsive editor;
- load and apply saved appearance globally through a dynamic MUI ThemeProvider;
- persist personal `system` / `light` / `dark` choice in localStorage;
- support presets plus manual token editing;
- show an isolated live preview for navigation, cards, form controls, table, buttons, and alerts;
- explain contrast failures returned by the backend;
- provide reset to defaults, cancel draft, copy JSON, import JSON, and export JSON;
- show save state, version conflicts, and appearance history.

## Typed controls

- primary, secondary, accent, background, paper, sidebar, app bar, primary text, secondary text, divider, success, warning, and error colors for light and dark schemes;
- safe font-family choice;
- normal or compact density;
- bounded component radius;
- contained, soft, or outlined button style;
- outlined, elevated, or flat card style;
- shadows enabled or disabled.

## Out of scope

- arbitrary CSS, uploaded fonts, or remote font URLs;
- document PDF/Excel appearance;
- module visibility;
- invitations, users, authentication, or authorization;
- SMTP or mail delivery;
- encrypted full-system configuration archives;
- applying an unsaved draft to the whole running application;
- per-user custom colors beyond display mode.

## Acceptance criteria

- saved appearance applies to the full application without restart;
- display mode follows system preference or explicit light/dark choice from localStorage;
- both schemes and all approved typed controls persist and reload;
- low-contrast text/surface combinations return a clear validation reason;
- stale writes return HTTP 409 and do not overwrite newer data;
- isolated preview updates immediately from the draft;
- presets, reset, cancel, copy, import, and export work on desktop and mobile;
- history contains field names only and no secret or unbounded payload data;
- Alembic has one head;
- backend, frontend, browser, PostgreSQL, Docker, document, and full exact-head Quality gates pass.