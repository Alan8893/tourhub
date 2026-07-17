# TourHub Project Status

Status date: 2026-07-17

## Current phase

The guided single-club preparation baseline and operator runbooks are complete. Ready PR #80 adds the validated production-like Docker runtime. Stacked Ready PR #81 audits the approved product specification and moves final migration/release hardening after the remaining release-blocking user and domain capabilities.

## Verified baseline

- `main`: `99d9c2d985b8a21c62fe148e07e08b3632ef961a` — merged PR #79.
- Alembic head: `h10007`.
- PR #77 merged as `18d4fabde3eda6c83c0c0f998e870a6f043e8dec` after Quality #416 and Document Quality #49.
- PR #78 passed retargeted exact-head Quality #431, Document Quality #63, and Guided Release Acceptance #14 and merged as `6332ef5f86973c7832e92dc1ef0a681cc4e17d1e`.
- PR #79 passed exact-head Quality #436, Document Quality #67, Guided Release Acceptance #18, and Operator Docs #4 and merged as `99d9c2d985b8a21c62fe148e07e08b3632ef961a`.
- PR #80 exact head `73b233f7529d5d310a750071d592e9b108b9a1df` passed Quality #454, Document Quality #84, Guided Release Acceptance #35, Operator Docs #21, and Docker Release Runtime #17 and is Ready for review.
- PR #81 exact head `93d11241729634a37ddfade2de6f88a1ab6e9387` passed Quality #458, Document Quality #88, Guided Release Acceptance #39, Operator Docs #25, and Docker Release Runtime #21 and is Ready for review.
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

### Ready PR #80 — Docker release runtime

- standalone `docker-compose.release.yml` without application source bind mounts;
- production frontend image built with Node and served by Nginx;
- same-origin `/api/` proxy plus frontend/backend health checks;
- PostgreSQL and Redis restricted to the internal Compose network;
- clean image build and disposable clean-environment startup;
- API project creation and persistence verification after application restart;
- Alembic current-head verification and focused Docker diagnostics.

## Product completeness findings — Ready PR #81

Implemented or release-ready:

- local one-club project preparation;
- participant-count recalculation;
- menu generation and authoritative manual editing;
- shopping, packaging, equipment, branding, and current document package;
- installation, backup/restore, and production-like Docker runtime.

Release-blocking gaps against the approved product specification:

- invitation-only users, roles, authentication, and backend authorization;
- CLUB/PERSONAL recipe ownership, variants, publication, and moderation;
- centralized backend alcohol prohibition across API and CSV import;
- actor-aware audit log;
- complete consolidated Russian PDF and workbook contents.

Scope decisions still required:

- instructor preference-based generation priority;
- preparation technology, tags, season compatibility, dietary restrictions, and richer recipe categories;
- exact boundary between first-release metadata and explicitly deferred enhancements.

## Next

1. Merge PR #80 only after a separate `Сливай` command and final merge recheck.
2. Complete and merge the product completeness audit after PR #80 is in `main` and PR #81 is synchronized.
3. Implement access foundation.
4. Implement recipe ownership and lifecycle.
5. Implement central alcohol prohibition.
6. Implement actor-aware audit logging.
7. Complete consolidated exports and role-based product acceptance.
8. Freeze the first-release schema and only then add the final migration cycle and release workflow.

## Quality debt

- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- optional recipe metadata decision and coverage;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
