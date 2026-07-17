# TourHub Project Status

Status date: 2026-07-17

## Current phase

The guided single-club preparation baseline, operator runbooks, and production-like Docker runtime are complete. The current documentation audit reconciles the approved product specification with the implemented application and records the Product Owner decision to implement a unified System Settings foundation before multi-user access.

## Verified baseline

- `main`: `939828e8c335966dde2d04c5083ee7d2da07c6eb` — merged PR #80.
- Alembic head: `h10007`.
- PR #77 merged as `18d4fabde3eda6c83c0c0f998e870a6f043e8dec`.
- PR #78 merged as `6332ef5f86973c7832e92dc1ef0a681cc4e17d1e`.
- PR #79 merged as `99d9c2d985b8a21c62fe148e07e08b3632ef961a`.
- PR #80 passed Quality #454, Document Quality #84, Guided Release Acceptance #35, Operator Docs #21, and Docker Release Runtime #17 and merged as `939828e8c335966dde2d04c5083ee7d2da07c6eb`.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented

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

## Product completeness findings

Implemented or release-ready:

- local one-club project preparation;
- participant-count recalculation;
- menu generation and authoritative manual editing;
- shopping, packaging, equipment, branding, and current document package;
- installation, backup/restore, and production-like Docker runtime.

Partial or missing against the approved product specification:

- unified system settings beyond the existing club name/logo branding;
- invitation-only users, roles, authentication, and backend authorization;
- CLUB/PERSONAL recipe ownership, variants, publication, and moderation;
- centralized backend alcohol prohibition across API and CSV import;
- actor-aware audit log;
- complete consolidated Russian PDF and workbook contents.

Scope decisions still required:

- exact System Settings sections and first implementation slice;
- appearance customization model and allowed branding controls;
- module settings and whether they enable/disable navigation or behavior;
- invitation configuration versus actual invitation/user workflow;
- mail provider, secret storage, sender identity, and test-delivery behavior;
- instructor preference priority and optional recipe metadata.

## Next

1. Complete and merge the product completeness audit.
2. Clarify and implement System Settings foundation as the next user-facing capability.
3. Implement access foundation and connect invitations to approved settings.
4. Implement recipe ownership and lifecycle.
5. Implement central alcohol prohibition.
6. Implement actor-aware audit logging.
7. Complete consolidated exports and product acceptance.
8. Freeze the schema and only then add the final migration cycle and release workflow.

## Quality debt

- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- optional recipe metadata decisions;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
