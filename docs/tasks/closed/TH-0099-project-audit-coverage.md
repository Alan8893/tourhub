# TH-0099 — Project Audit Coverage

Status: DONE

Started: 2026-07-19

Completed: 2026-07-19

## Goal

Add semantic actor-attributed audit events to Project creation, updates, and preparation while preserving existing behavior.

## Delivered

- `project_created` shares the Project creation commit;
- `project_participants_updated` shares the participant and derived-data recalculation transaction;
- `project_generation_mode_updated` shares the Project update commit;
- `project_prepared` shares one caller-owned transaction with purchase list, checklist, and equipment preparation;
- events use the authenticated preparation actor and bounded Project snapshots;
- no-op participant and generation-mode updates create no event;
- failed creation, recalculation, audit recording, or preparation rolls back both domain changes and pending audit events;
- standalone purchase, checklist, and equipment creation retains its previous commit behavior by default;
- the Administrator Audit UI/API exposes Russian Project labels and filtering;
- no menu/MealSlot or unrelated audit domain was added.

## Verification

Candidate head `6cccd03d0643f39425a3c4be59339f046d381f46` passed:

- strict Ruff and mypy for affected Project, repository, preparation, and audit paths;
- all 325 Backend tests, including success, no-op, actor attribution, and rollback scenarios;
- Frontend unit tests, production build, and complete browser acceptance;
- Product Acceptance with focused Project audit API tests and the real-Chrome Audit flow;
- PostgreSQL backup/restore and Alembic single-head validation;
- Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness.

A final exact-head workflow run follows the documentation-only task closure.

## Excluded

- menu generation and manual MealSlot audit;
- settings, mail, invitations, import, shopping, equipment, or document audit expansion outside the preparation orchestration event;
- ORM-wide audit, undo, replay, export, retention, or external integrations;
- migrations, architecture changes, new Project capabilities, or release-tag movement.
