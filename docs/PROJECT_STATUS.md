# TourHub Project Status

Status date: 2026-07-17

## Current phase

The guided single-club preparation baseline, operator runbooks, production-like Docker runtime, product completeness audit, club settings, site appearance, and document appearance are complete. Draft PR #87 implements typed module navigation visibility with backend dependency locks.

## Verified baseline

- `main`: `18d5c9637e2e692b630009167dd622ee40ee2747` — merged PR #86.
- `main` Alembic head: `h10010`.
- PR #77 merged as `18d4fabde3eda6c83c0c0f998e870a6f043e8dec`.
- PR #78 merged as `6332ef5f86973c7832e92dc1ef0a681cc4e17d1e`.
- PR #79 merged as `99d9c2d985b8a21c62fe148e07e08b3632ef961a`.
- PR #80 merged as `939828e8c335966dde2d04c5083ee7d2da07c6eb`.
- PR #83 merged as `950a43914230f6fe4be3bf217a4e5f1b79e7265f`.
- PR #84 merged as `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a`.
- PR #85 merged as `0e4e376470072e9475a31504faeb46e8b5a68364`.
- PR #86 passed Quality #575, Document Quality #201, Guided Release Acceptance #152, Operator Docs #138, and Docker Release Runtime #133 before merge.
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
- System Settings is scheduled before multi-user access;
- basic migration, backup/restore, Docker, and full Quality gates remain mandatory during feature work.

### System Settings foundation

- dedicated responsive `/settings` route and independent typed section ownership through ADR-014;
- `ClubSettings` through additive Alembic `h10008`;
- `AppearanceSettings` through `h10009` with dynamic light/dark themes and safe theme transfer;
- `DocumentAppearanceSettings` through `h10010` with one immutable rendering snapshot;
- optimistic versioning, PostgreSQL row locking, HTTP 409 conflicts, and safe local-admin history;
- existing club/document compatibility contracts remain preserved.

## Draft PR #87 — System Settings module visibility

Backend:

- additive Alembic `h10011` creates independent singleton `module_settings` persistence;
- explicit boolean columns own project, catalogue, import, shopping, equipment, and document visibility;
- projects and catalogue are required and cannot be hidden;
- visible documents require visible shopping and equipment;
- versioned updates use a PostgreSQL row lock and reject stale editors with HTTP 409;
- module history records changed field names only and shares the latest-200 retention boundary;
- API metadata includes Russian labels, descriptions, dependencies, required state, and lock reasons.

Frontend:

- the planned `Модули` section becomes a working responsive editor;
- required and dependency-locked switches explain why they cannot be changed;
- reset, cancel, save, validation, conflict, version, and history states are shown in Russian;
- saved visibility updates desktop/mobile sidebar navigation immediately;
- shopping, purchase, equipment, and document project cards follow the same global snapshot;
- direct routes and APIs remain unchanged and accessible.

Architecture:

- module visibility is presentation policy, not authorization or runtime backend module unloading;
- `Настройки`, required projects, and required catalogue navigation remain visible;
- future roles and backend authorization will be separate enforcement layers.

## Remaining System Settings sequence

1. Typed future invitation policy fields without a functional invitation list.
2. Informative mail boundary until access foundation exists.
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

- finish exact-head validation and review for PR #87;
- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.