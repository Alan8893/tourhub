# TourHub Project Status

Status date: 2026-07-17

## Current phase

The guided single-club preparation baseline, operator runbooks, production-like Docker runtime, and product completeness audit are complete. Draft PR #84 implements the first System Settings slice: a dedicated settings shell and a typed, versioned club profile that preserves existing branding behavior.

## Verified baseline

- `main`: `950a43914230f6fe4be3bf217a4e5f1b79e7265f` — merged PR #83.
- `main` Alembic head: `h10007`.
- PR #77 merged as `18d4fabde3eda6c83c0c0f998e870a6f043e8dec`.
- PR #78 merged as `6332ef5f86973c7832e92dc1ef0a681cc4e17d1e`.
- PR #79 merged as `99d9c2d985b8a21c62fe148e07e08b3632ef961a`.
- PR #80 passed Quality #454, Document Quality #84, Guided Release Acceptance #35, Operator Docs #21, and Docker Release Runtime #17 and merged as `939828e8c335966dde2d04c5083ee7d2da07c6eb`.
- PR #83 passed Quality #464, Document Quality #93, Guided Release Acceptance #44, Operator Docs #30, and Docker Release Runtime #25 and merged as `950a43914230f6fe4be3bf217a4e5f1b79e7265f`.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented on main

### Guided project preparation

- project creation, participants, duration, meal boundaries, and role-aware menu generation;
- authoritative manual editing and persisted generation warnings;
- persisted shopping, packaging, checklist, surplus, and responsible-person text;
- persisted equipment requirements, aggregation, manual rows, overrides, removals, and transactional refresh;
- Russian purchase/equipment PDF, Excel, print, and complete ZIP;
- singleton club name and validated PNG/JPEG logo branding;
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

## Draft PR #84 — System Settings club foundation

Backend:

- additive Alembic `h10008` expands the singleton `club_settings` record and adds safe settings history;
- club name remains required and all approved profile fields are optional;
- main/light/dark logos, square icon, favicon, login background, and document image are persisted;
- PNG/JPEG/WebP content, MIME type, dimensions, and per-kind limits are validated by the backend;
- SVG is rejected;
- versioned updates reject stale editors with HTTP 409;
- successful changes record safe field names, local-admin attribution, resulting version, and timestamp;
- only the latest 200 focused settings-history rows are retained;
- legacy `/api/v1/club-settings` and existing document-brand snapshots remain compatible.

Frontend:

- `/settings` is available from the main desktop and mobile navigation;
- the desktop settings page uses vertical section navigation and mobile uses a section selector;
- club settings are removed from the project workspace;
- the club section edits all profile fields, labelled social links, and approved image types;
- future Appearance, Documents, Modules, Invitations, and Mail sections are visible as honest planned boundaries;
- conflict, validation, saving, version, and history states are shown in Russian.

Architecture:

- ADR-014 defines one settings surface with independent typed section ownership;
- `ClubSettings` is not used as an unrelated settings god object;
- arbitrary CSS, unrestricted settings JSON, generic key/value storage, and visible database secrets are rejected.

## Remaining System Settings sequence

1. Site appearance and preview.
2. Separate document appearance.
3. Module navigation visibility, dependency locks, and future invitation/mail configuration boundaries.
4. Access foundation and functional invitations.
5. Working SMTP delivery after identity exists.

## Other release-blocking work

- CLUB/PERSONAL recipe ownership, variants, publication, and moderation;
- centralized backend alcohol prohibition across API and CSV import;
- actor-aware application audit log;
- complete consolidated Russian PDF and workbook contents;
- active deployment catalogue and import acceptance;
- optional recipe metadata and preference-priority decisions.

## Quality debt

- finish exact-head validation and review for PR #84;
- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
