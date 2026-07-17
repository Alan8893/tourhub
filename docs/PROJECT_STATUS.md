# TourHub Project Status

Status date: 2026-07-17

## Current phase

The TH-0061 guided single-club preparation workflow is complete. Merged PR #79 adds the operator installation, update, backup, restore, and recovery path. Draft PR #80 adds the immutable Docker image build and production-like runtime validation slice.

## Verified baseline

- `main`: `99d9c2d985b8a21c62fe148e07e08b3632ef961a` — merged PR #79.
- Alembic head: `h10007`.
- PR #77 merged as `18d4fabde3eda6c83c0c0f998e870a6f043e8dec` after Quality #416 and Document Quality #49.
- PR #78 passed retargeted exact-head Quality #431, Document Quality #63, and Guided Release Acceptance #14 and merged as `6332ef5f86973c7832e92dc1ef0a681cc4e17d1e`.
- PR #79 passed exact-head Quality #436, Document Quality #67, Guided Release Acceptance #18, and Operator Docs #4 and merged as `99d9c2d985b8a21c62fe148e07e08b3632ef961a`.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented

### Guided project preparation — completed TH-0061

- project creation, participants, duration, meal boundaries, and role-aware menu generation;
- persisted purchase list, checklist, packaging, surplus, and purchasing contact;
- persisted equipment requirements, aggregation, manual rows, overrides, removals, and transactional refresh;
- Russian purchase/equipment PDF, Excel, print, and complete project ZIP;
- singleton club name and validated PNG/JPEG logo branding;
- preparation readiness restored after reload without repeated calculation;
- equipment-aware completion state and clean unprepared states;
- full desktop/mobile create → menu → prepare → reload → branded ZIP release acceptance.

### Operator installation and update — completed TH-0071

- installation prerequisites, first start, health, migration, LAN, port, and volume verification;
- backup-first update flow with explicit Alembic migration before application restart;
- host-side PostgreSQL custom-format backup script;
- confirmed restore script with an automatic pre-restore safety dump;
- rollback boundaries prohibiting destructive volume deletion and ad hoc production downgrades;
- focused Operator Docs validation for shell syntax/help, required commands, links, and Compose syntax.

### Draft PR #80 — Docker release runtime

- standalone `docker-compose.release.yml` without application source bind mounts;
- production frontend image built with Node and served by Nginx;
- same-origin `/api/` proxy plus frontend/backend health checks;
- PostgreSQL and Redis restricted to the internal Compose network;
- clean image build and disposable clean-environment startup;
- API project creation and persistence verification after application restart;
- Alembic current-head verification and focused Docker diagnostics.

## Next

1. Complete PR #80 exact-head Quality and Docker release runtime validation.
2. Add PostgreSQL migration upgrade/downgrade smoke.
3. Complete the final release workflow and release checklist.
4. Add invitation-only access only after the local single-user release is validated.

## Quality debt

- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- PostgreSQL migration smoke;
- final release workflow.
