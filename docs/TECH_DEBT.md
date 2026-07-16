# TourHub Technical Debt

Status date: 2026-07-16

Technical debt is prioritized by product risk.

## P0 — Release blockers

No open P0 release blockers are recorded after TH-0070 / PR #54.

## P1 — Quality and maintainability

### TD-005 — Ruff backlog

The audited snapshot contained 195 Ruff violations. Critical and selected workflow baselines are enforced.

### TD-006 — Strict mypy backlog

The audited snapshot contained 74 strict mypy errors. Selected project, menu, shopping, and equipment workflow modules are clean and enforced.

### TD-007 — Frontend and browser automated tests

Coverage includes menu editing, Dish classification, catalogue readiness, navigation, editable purchase progress, package review, purchasing-contact persistence, equipment formatting, responsive no-overflow checks, and screenshots.

Draft PR #73 adds real-browser coverage for persisted project equipment loading, summary quantities, exact API access, and 360 px layout.

Remaining critical coverage:

- complete guided project preparation;
- active deployment catalogue acceptance data;
- catalogue import interaction and error rendering;
- final end-to-end release acceptance.

### TD-008 — Continuous Integration

Implemented gates include backend tests, Ruff/mypy, Alembic single-head, frontend tests/build/audit, browser acceptance, build diagnostics, and PostgreSQL backup/restore.

Remaining:

- PostgreSQL migration upgrade/downgrade smoke;
- Docker image/build validation;
- final release-acceptance workflow.

### TD-010 — Documentation and ADR consistency

Canonical status, roadmap, technical debt, and TH-0061 are synchronized through merged PR #72 and draft PR #73. ADR-013 remains authoritative for Dish role and meal-type ownership.

### TD-024 — Legacy MealPlanSlot compatibility

MealSlot is primary. MealPlanItem remains persisted for compatibility. Consumer audit and approved removal planning remain required.

## P2 — Product completion debt

### TD-002 — Multi-user authorization baseline

Invitation-only registration, authentication, roles, ownership, and administration remain deferred until single-user acceptance.

### TD-011 — Recipe ownership and moderation

CLUB/PERSONAL ownership, variants, publication review, and moderation remain later work.

### TD-012 — Meal composition and diversity

Approved implementation is merged through PR #69. Remaining work is operational catalogue maintenance or future requirement-dependent preference modes.

### TD-013 — Equipment domain completion

Draft PR #73 delivers:

- persisted recipe equipment requirements;
- validated add, update, and delete API;
- persisted project EquipmentList;
- sum within one meal occurrence and maximum simultaneous aggregation across occurrences;
- safe repeated regeneration;
- Russian recipe and project review UI;
- backend, unit, build, browser, and mobile coverage.

Remaining after PR #73:

- project-level manual additions and removals;
- manual quantity overrides;
- preservation of overrides during recalculation;
- automatic refresh after participant, menu, and recipe mutations;
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

Merged PRs #70–#72 deliver editable purchase progress, package review, surplus, and the optional purchasing contact with recalculation preservation.

Remaining:

- complete guided-preparation acceptance;
- verify recalculation visibility without losing user progress.

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
