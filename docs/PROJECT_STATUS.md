# TourHub Project Status

Status date: 2026-07-17

## Current phase

The guided single-club preparation baseline, operator runbooks, production-like Docker runtime, product completeness audit, and first System Settings slice are complete. Draft PR #85 implements the second settings slice: safe organization-wide site appearance with personal display-mode selection and isolated preview.

## Verified baseline

- `main`: `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a` — merged PR #84.
- `main` Alembic head: `h10008`.
- PR #77 merged as `18d4fabde3eda6c83c0c0f998e870a6f043e8dec`.
- PR #78 merged as `6332ef5f86973c7832e92dc1ef0a681cc4e17d1e`.
- PR #79 merged as `99d9c2d985b8a21c62fe148e07e08b3632ef961a`.
- PR #80 merged as `939828e8c335966dde2d04c5083ee7d2da07c6eb`.
- PR #83 merged as `950a43914230f6fe4be3bf217a4e5f1b79e7265f`.
- PR #84 passed Quality #499, Document Quality #127, Guided Release Acceptance #78, Operator Docs #64, and Docker Release Runtime #59 before merge.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented on main

### Guided project preparation

- project creation, participants, duration, meal boundaries, and role-aware menu generation;
- authoritative manual editing and persisted generation warnings;
- persisted shopping, packaging, checklist, surplus, and responsible-person text;
- persisted equipment requirements, aggregation, manual rows, overrides, removals, and transactional refresh;
- Russian purchase/equipment PDF, Excel, print, and complete ZIP;
- reload-safe preparation readiness and equipment-aware completion;
- full desktop/mobile create → menu → prepare → reload → branded ZIP acceptance.

### Operations and runtime

- installation, update, backup, restore, recovery, health, migration, LAN, port, and volume guidance;
- production-like release Compose without application bind mounts;
- production frontend image served by Nginx;
- internal PostgreSQL and Redis networking;
- same-origin API proxy and health checks;
- clean image build/start, Alembic head, API persistence after restart, diagnostics, and cleanup.

### Product sequencing

- approved product areas have an evidence-based completeness status;
- final migration downgrade/re-upgrade smoke is placed after feature freeze;
- System Settings is scheduled before multi-user access by Product Owner decision;
- basic migration, backup/restore, Docker, and full Quality gates remain mandatory throughout feature development.

### System Settings club foundation

- dedicated responsive `/settings` route and main navigation entry;
- independent typed settings-section ownership through ADR-014;
- singleton club profile with one required name and optional identity/contact/location fields;
- seven validated PNG/JPEG/WebP image roles and no SVG;
- optimistic versioning, PostgreSQL row locking, HTTP 409 conflicts, and safe local-admin history;
- existing document branding and legacy `/api/v1/club-settings` compatibility;
- additive Alembic `h10008` with one head.

## Draft PR #85 — System Settings appearance

Backend:

- additive Alembic `h10009` creates independent singleton `appearance_settings` persistence;
- typed light/dark token sets and safe enums own appearance configuration;
- TourHub, Forest, Ocean, and Sunset presets provide validated starting points;
- backend validates #RRGGBB values and minimum text/surface contrast with a clear Russian reason;
- versioned updates use a PostgreSQL row lock and reject stale editors with HTTP 409;
- appearance history records changed field names only and shares the global latest-200 retention boundary.

Frontend:

- saved appearance is applied globally through one dynamic MUI ThemeProvider without restart;
- each browser stores only `system`, `light`, or `dark` preference in localStorage;
- the organization controls colors, safe font stack, density, radius, button/card styles, and shadows;
- the settings page provides presets, full token editing, isolated light/dark preview, reset, cancel, copy, import, and export;
- imported theme JSON is versioned and validated before it can enter preview state;
- an unsaved draft never changes the rest of the running application;
- desktop and mobile browser acceptance is independent from the existing club-settings scenario.

Architecture:

- `AppearanceSettings` remains independent from `ClubSettings` and future document/module/mail models;
- arbitrary CSS, external fonts, uploaded font files, and unrestricted key/value settings remain prohibited;
- the future user preference model will replace localStorage without changing global organization tokens.

## Remaining System Settings sequence

1. Separate document appearance.
2. Module navigation visibility, dependency locks, and future invitation/mail configuration boundaries.
3. Access foundation and functional invitations.
4. Working SMTP delivery after identity exists.

## Other release-blocking work

- CLUB/PERSONAL recipe ownership, variants, publication, and moderation;
- centralized backend alcohol prohibition across API and CSV import;
- actor-aware application audit log;
- complete consolidated Russian PDF and workbook contents;
- active deployment catalogue and import acceptance;
- optional recipe metadata and preference-priority decisions.

## Quality debt

- finish exact-head validation and review for PR #85;
- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
