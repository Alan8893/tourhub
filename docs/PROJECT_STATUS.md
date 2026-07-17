# TourHub Project Status

Status date: 2026-07-17

## Current phase

The guided single-club preparation baseline, operator runbooks, production-like Docker runtime, product completeness audit, club settings, and site appearance are complete. Draft PR #86 implements the third System Settings slice: independent document appearance applied through one immutable generation snapshot.

## Verified baseline

- `main`: `0e4e376470072e9475a31504faeb46e8b5a68364` — merged PR #85.
- `main` Alembic head: `h10009`.
- PR #77 merged as `18d4fabde3eda6c83c0c0f998e870a6f043e8dec`.
- PR #78 merged as `6332ef5f86973c7832e92dc1ef0a681cc4e17d1e`.
- PR #79 merged as `99d9c2d985b8a21c62fe148e07e08b3632ef961a`.
- PR #80 merged as `939828e8c335966dde2d04c5083ee7d2da07c6eb`.
- PR #83 merged as `950a43914230f6fe4be3bf217a4e5f1b79e7265f`.
- PR #84 merged as `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a`.
- PR #85 passed Quality #537, Document Quality #164, Guided Release Acceptance #115, Operator Docs #101, and Docker Release Runtime #96 before merge.
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

### System Settings site appearance

- independent singleton `AppearanceSettings` through Alembic `h10009`;
- complete organization-wide light and dark token sets;
- safe presets, fonts, density, radius, component styles, and shadow controls;
- backend #RRGGBB and contrast validation with Russian explanations;
- dynamic global MUI theme application without restart;
- per-browser system/light/dark mode in localStorage;
- isolated preview, reset, cancel, copy, validated JSON import, and JSON export;
- optimistic conflicts, row locking, safe history, and desktop/mobile acceptance.

## Draft PR #86 — System Settings document appearance

Backend:

- additive Alembic `h10010` creates independent singleton `document_appearance_settings` persistence;
- typed palette, logo source, contacts visibility, footer, title image, and table-density settings;
- backend validates #RRGGBB values and minimum table-header contrast with a clear Russian reason;
- versioned updates use a PostgreSQL row lock and reject stale editors with HTTP 409;
- document history records changed field names only and shares the latest-200 retention boundary;
- selected missing images fall back to the main logo, while `none` suppresses the logo explicitly.

Document pipeline:

- one frozen snapshot combines `ClubSettings` with `DocumentAppearanceSettings`;
- `ProjectDocumentService` loads that snapshot once per generation request;
- purchase/equipment PDF, Excel, printable text, and all ZIP entries reuse the same object;
- PDF and Excel share centralized palette/density/rendering helpers;
- existing routes, content types, and filenames remain compatible;
- consolidated document contents remain outside this slice.

Frontend:

- the planned `Документы` section becomes a working responsive editor;
- the form edits palette, logo source, contacts, footer, title background, and table density;
- an isolated document preview shows the draft before save;
- reset, cancel, save, validation, conflict, version, and history states are shown in Russian;
- desktop/mobile browser acceptance is independent from club and site appearance scenarios.

## Remaining System Settings sequence

1. Module navigation visibility and required dependency locks.
2. Future invitation and mail configuration boundaries.
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

- finish exact-head validation and review for PR #86;
- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
