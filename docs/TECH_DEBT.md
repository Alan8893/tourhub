# TourHub Technical Debt

Status date: 2026-07-16

Technical debt is prioritized by product risk.

## P0 — Release blockers

No open P0 release blockers are recorded after TH-0070 / PR #54.

## P1 — Quality and maintainability

### TD-005 — Ruff backlog

The audited snapshot contained 195 Ruff violations. Critical and selected project, menu, shopping, and equipment workflow baselines are enforced.

### TD-006 — Strict mypy backlog

The audited snapshot contained 74 strict mypy errors. Selected project, menu, shopping, equipment override, regeneration, and recipe-recalculation modules are clean and enforced.

### TD-007 — Frontend and browser automated tests

Coverage includes menu editing, Dish classification, catalogue readiness, purchasing review, equipment aggregation, project equipment CRUD, mutation refetch, responsive no-overflow checks, and screenshots.

Merged PR #74 covers project-level equipment overrides. Draft PR #75 adds backend acceptance for direct recipe-equipment changes across multiple prepared projects and transaction rollback on refresh failure.

Remaining critical coverage:

- active deployment catalogue acceptance data;
- catalogue import interaction and error rendering;
- final end-to-end release acceptance.

### TD-008 — Continuous Integration

Implemented gates include backend tests, stabilized Ruff and strict mypy, Alembic single-head, frontend tests/build/audit, browser acceptance, build diagnostics, and PostgreSQL backup/restore.

Remaining:

- PostgreSQL migration upgrade/downgrade smoke;
- Docker image/build validation;
- final release-acceptance workflow.

### TD-010 — Documentation and ADR consistency

Canonical status, roadmap, technical debt, and TH-0061 are synchronized through merged PR #74 and draft PR #75. ADR-013 remains authoritative for Dish role and meal-type ownership.

### TD-024 — Legacy MealPlanItem compatibility

MealSlot is primary. MealPlanItem remains persisted for compatibility. Consumer audit and approved removal planning remain required.

## P2 — Product completion debt

### TD-002 — Multi-user authorization baseline

Invitation-only registration, authentication, roles, ownership, and administration remain deferred until single-user acceptance.

### TD-011 — Recipe ownership and moderation

CLUB/PERSONAL ownership, variants, publication review, and moderation remain later work.

### TD-012 — Meal composition and diversity

Approved implementation is merged through PR #69. Remaining work is operational catalogue maintenance or future requirement-dependent preference modes.

### TD-013 — Equipment domain completion

Merged PRs #73 and #74 deliver persisted recipe requirements, maximum-simultaneous aggregation, project editing, override preservation, recalculation after menu and participant changes, Russian UI, and browser/mobile coverage.

Draft PR #75 delivers:

- refresh after direct recipe-equipment requirement POST, PUT, and DELETE;
- multi-project fan-out for every prepared EquipmentList using the recipe;
- one transaction for source mutation and derived refresh;
- preservation of overrides, removals, and manual rows;
- no implicit EquipmentList creation for unprepared projects;
- rollback coverage when refresh fails.

Remaining after PR #75:

- equipment export in final Russian documents.

### TD-014 — Export templates and branding

Complete Russian PDF/Excel templates, equipment contents, and club branding.

### TD-015 — Audit log

Record actor/action/time metadata when multi-user access is introduced.

### TD-019 — Dish recipe change impact preview

Show affected plans and purchasing/equipment projections before recipe replacement.

### TD-020 — Centralized product-policy validation

Apply approved product restrictions consistently across product, recipe, Dish, and import validation.

### TD-025 — Complete Product CRUD

Product update and guarded delete remain unimplemented.

### TD-026 — Shopping and packaging review

Merged PRs #70–#72 deliver editable purchase progress, package review, surplus, and the purchasing contact with recalculation preservation.

Remaining:

- complete guided-preparation acceptance;
- verify all derived-document updates remain visible without losing user progress.

## Completed history

- TD-001 — accidental public API placeholders removed.
- TD-003 — transactional purchasing refresh implemented.
- TD-004 — local stack and primary workflow stabilized.
- TD-009 — dependency audit passes at moderate severity.
- TD-016 — backup/restore CI implemented.
- TD-017 — Meal Plan Editor acceptance completed.
- TD-018 — Dish catalogue and active-recipe assignment implemented.
- TD-021 — MealSlot relation identifiers repaired.
- TD-022 — invalid pseudo cooldown removed.
- TD-023 — backend meal-boundary authority delivered.
