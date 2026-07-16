# TourHub Technical Debt

Status date: 2026-07-16

Technical debt is prioritized by product risk.

## P0 — Release blockers

No open P0 release blockers are recorded after TH-0070 / PR #54.

## P1 — Quality and maintainability

### TD-005 — Ruff backlog

The audited snapshot contained 195 Ruff violations. Critical and selected workflow baselines are enforced.

### TD-006 — Strict mypy backlog

The audited snapshot contained 74 strict mypy errors. Selected project, menu, and shopping modules are clean and enforced.

### TD-007 — Frontend and browser automated tests

Coverage includes menu editing, Dish classification, catalogue readiness, navigation, editable purchase progress, package review, responsive no-overflow checks, and screenshots.

PR #72 adds pure and browser coverage for saving, refetching, clearing, and mobile presentation of the optional purchasing contact.

Remaining critical coverage:

- complete guided project preparation;
- active deployment catalogue acceptance data;
- catalogue import interaction and error rendering;
- final end-to-end release acceptance.

### TD-008 — Continuous Integration

Implemented gates include backend tests, Ruff/mypy, Alembic single-head, frontend tests/build/audit, browser acceptance, and PostgreSQL backup/restore.

Remaining:

- PostgreSQL migration upgrade/downgrade smoke;
- Docker image/build validation;
- final release-acceptance workflow.

### TD-010 — Documentation and ADR consistency

Canonical status, roadmap, technical debt, and TH-0061 are synchronized through merged PR #71 and draft PR #72. ADR-013 remains authoritative for Dish role and meal-type ownership.

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

Persist recipe equipment requirements, aggregate maximum simultaneous need, support manual overrides, and join equipment to recalculation.

### TD-014 — Export templates and branding

Complete Russian PDF/Excel templates and club branding.

### TD-015 — Audit log

Record actor/action/time metadata when multi-user access is introduced.

### TD-019 — Dish recipe change impact preview

Show affected plans and purchasing projections before recipe replacement.

### TD-020 — Centralized product-policy validation

Apply approved product restrictions consistently across product, recipe, Dish, and import validation.

### TD-025 — Complete Product CRUD

Product update and guarded delete remain unimplemented.

### TD-026 — Shopping and packaging review

Merged PR #70 delivers editable required/purchased/remaining review. Merged PR #71 delivers package size, count, total quantity, and surplus review.

Draft PR #72 delivers:

- optional purchasing contact persisted on PurchaseList;
- trim, clear, and length validation;
- preservation during item recalculation;
- Russian save/clear UI and browser coverage.

Remaining after PR #72:

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
