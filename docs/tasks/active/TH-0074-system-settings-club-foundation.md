# TH-0074 — System Settings Club Foundation

Status: IN PROGRESS

Last updated: 2026-07-17

## Goal

Create the dedicated `/settings` foundation and move club identity configuration out of the project workspace into a typed, versioned settings section that can safely grow into appearance, document, module, invitation, and mail settings.

## Product decisions

- the user-facing page is named `Настройки` and is available at `/settings`;
- the main sidebar contains the settings entry;
- until authorization exists, the page is locally accessible but prepared for future Administrator-only access;
- the first implementation slice covers the settings shell and club profile only;
- `club_name` remains the only required club field;
- all other profile fields are optional;
- images support PNG, JPEG, and WebP only; SVG is excluded;
- version-based conflict protection is required;
- the latest 200 settings-history records are retained;
- changes are attributed to `Локальный администратор` until identity exists;
- image and scalar changes must not expose binary data in history or logs.

## Scope

### Frontend

- add `/settings` route and `Настройки` in the main sidebar;
- add responsive section navigation: vertical navigation on desktop and select control on mobile;
- implement the `Клуб` section and planned placeholders for later sections;
- remove the project-workspace club-settings widget;
- edit and save club profile independently from future sections;
- upload, preview, replace, and remove supported club images;
- show saved state, validation errors, stale-version conflicts, and history;
- keep future access, appearance, documents, modules, invitations, and mail sections explicitly separated.

### Backend

- extend the existing singleton `club_settings` model instead of introducing an untyped settings JSON blob;
- add optional short name, legal name, description, address, phone, email, website, social links, timezone, city, and region;
- add main, light, and dark logos, square icon, favicon, login background, and document image;
- preserve the existing club branding API and document behavior;
- add a typed versioned settings API for the new page;
- reject updates based on a stale expected version with HTTP 409;
- record safe settings change history and retain the latest 200 rows;
- validate image MIME type, decoded content, dimensions, and per-kind size limits;
- add one additive Alembic migration with a single head.

## Image limits

- main, light, and dark logo: 2 MB each;
- square icon and favicon: 512 KB each;
- login background and document image: 5 MB each;
- accepted MIME types: `image/png`, `image/jpeg`, `image/webp`.

## Out of scope

- appearance design tokens and live theme preview;
- document appearance controls;
- module visibility settings;
- functional invitations, users, or authentication;
- working mail configuration or test delivery;
- encrypted configuration archive import/export;
- full actor-aware audit log;
- arbitrary CSS or SVG uploads.

## Acceptance criteria

- `/settings` is reachable from desktop and mobile navigation;
- only club name is required;
- all approved optional fields persist and reload;
- each approved image kind validates, persists, previews, removes, and reloads;
- main logo continues to brand existing PDF, Excel, print, and ZIP outputs;
- stale updates return HTTP 409 and do not overwrite newer values;
- successful updates append a safe history record attributed to `Локальный администратор`;
- no history row contains image bytes, data URLs, passwords, tokens, or future secret values;
- the service retains at most 200 history records;
- old `/club-settings` API behavior remains compatible;
- project workspace no longer embeds club settings;
- backend, frontend, API, migration, browser, document, Docker, and full Quality gates pass on the exact PR head.
