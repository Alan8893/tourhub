# TourHub Project Status

Status date: 2026-07-17

## Current phase

The TH-0061 guided single-club preparation workflow is complete. Merged PRs #77 and #78 add persistent club branding, reload-safe preparation readiness, and full desktop/mobile create-to-branded-ZIP acceptance. Draft PR #79 adds the operator installation, update, backup, restore, and recovery runbooks.

## Verified baseline

- `main`: `6332ef5f86973c7832e92dc1ef0a681cc4e17d1e` — merged PR #78.
- Alembic head: `h10007`.
- PR #77 merged as `18d4fabde3eda6c83c0c0f998e870a6f043e8dec` after Quality #416 and Document Quality #49.
- PR #78 passed retargeted exact-head Quality #431, Document Quality #63, and Guided Release Acceptance #14 and merged as `6332ef5f86973c7832e92dc1ef0a681cc4e17d1e`.
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

### Draft PR #79 — operator runbooks

- installation prerequisites, first start, health, migration, LAN, port, and volume verification;
- backup-first update flow with explicit Alembic migration before application restart;
- host-side PostgreSQL custom-format backup script;
- confirmed restore script with an automatic pre-restore safety dump;
- rollback boundaries prohibiting destructive volume deletion and ad hoc production downgrades;
- README operator entry points;
- focused Operator Docs gate for shell syntax/help, required commands, relative links, and Docker Compose syntax.

## Next

1. Complete Docker image build/runtime validation.
2. Add PostgreSQL migration upgrade/downgrade smoke.
3. Complete the final release workflow and release checklist.
4. Add invitation-only access only after the local single-user release is validated.

## Quality debt

- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- Docker build/runtime validation;
- PostgreSQL migration smoke;
- final release workflow.
