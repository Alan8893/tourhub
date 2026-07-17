# TH-0074 — System Settings Club Foundation

Status: DONE

Completed: 2026-07-17

Merged PR: #84

Merge commit: `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a`

## Goal

Create the dedicated `/settings` foundation and move club identity configuration out of the project workspace into a typed, versioned settings section that can safely grow into appearance, document, module, invitation, and mail settings.

## Delivered

- dedicated responsive `/settings` page and main-navigation entry;
- typed singleton club profile with the club name as the only required field;
- optional identity, contact, location, social-link, and image settings;
- PNG/JPEG/WebP validation with per-kind size limits and no SVG support;
- optimistic versioning, PostgreSQL row locking, HTTP 409 stale-write protection;
- safe local-administrator history retaining the latest 200 records;
- additive Alembic `h10008` with one head;
- compatibility for the legacy club-settings API and current document branding;
- full backend, frontend, browser, document, PostgreSQL, Docker, and exact-head Quality gates.

## Follow-up

TH-0075 implements site appearance, saved light/dark design tokens, per-browser display-mode preference, contrast validation, theme preview, reset, copy, import, and export.