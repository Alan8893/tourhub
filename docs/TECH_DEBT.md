# TourHub Technical Debt

Status date: 2026-07-16

Technical debt is prioritized by product risk.

## P0 — Release blockers

No open P0 release blockers are recorded after TH-0070 / PR #54.

## P1 — Quality and maintainability

### TD-005 — Ruff backlog

The audited snapshot contained 195 Ruff violations. Critical and selected workflow baselines are enforced. Continue expanding coverage without increasing debt.

### TD-006 — Strict mypy backlog

The audited snapshot contained 74 strict mypy errors. Selected project, menu, and shopping workflow modules are clean and enforced.

### TD-007 — Frontend and browser automated tests

Current coverage includes pure state, commands, validation, ordering, formatting, summaries, feedback, and responsive-policy helpers.

Real-browser coverage includes:

- MealSlot add, replace, and remove operations;
- Dish role and meal-type classification;
- catalogue-readiness refresh;
- responsive application navigation;
- purchase checklist loading and PATCH mutations;
- required, purchased, and remaining quantity refresh;
- package-count and package-surplus presentation in draft PR #71;
- desktop, tablet, and 360 px no-overflow checks and screenshots.

Remaining critical coverage:

- complete guided project preparation;
- active deployment catalogue acceptance data;
- catalogue import interaction and error rendering;
- final end-to-end release acceptance.

### TD-008 — Continuous Integration

Implemented gates include backend tests, selected Ruff/mypy, Alembic single-head, frontend tests/build/audit, browser acceptance suites, and PostgreSQL backup/restore.

Remaining:

- explicit migration upgrade/downgrade smoke against PostgreSQL;
- Docker image/build validation;
- final release-acceptance workflow.

### TD-010 — Documentation and ADR consistency

Canonical status, roadmap, active menu task, and TH-0061 task are synchronized through merged PR #70 and draft PR #71. ADR-013 remains authoritative for persisted role and meal-type ownership. ADR-006 is superseded where it described MealPlanItem as primary.

Historical archive documents and duplicate ADR history still require explicit canonical labelling where ambiguity remains.

### TD-024 — Legacy MealPlanItem compatibility

MealSlot is primary. MealPlanItem remains persisted for compatibility and increases mapping and recalculation complexity.

Required later:

- identify remaining consumers;
- verify legacy-only recalculation behavior;
- create a migration/removal plan;
- remove duplicate persistence only through an approved compatibility change.

## P2 — Product completion debt

### TD-002 — Multi-user authorization baseline

Invitation-only registration, secure local authentication, roles, recipe ownership, and administration are deferred until the single-user workflow is accepted.

### TD-011 — Recipe ownership and moderation

Remaining work covers CLUB/PERSONAL ownership, multiple recipe variants, publication review, and verified-instructor moderation.

### TD-012 — Meal composition and diversity

Approved implementation is merged through PR #69:

- normalized Dish-owned role and meal-type compatibility;
- role-aware production generation;
- same-day uniqueness and calendar-day three-day `main` diversity;
- authoritative manual slots across regeneration;
- persisted generation-warning snapshot and later reads.

Remaining work is operational or requirement-dependent:

- maintain explicit classification of the active deployment catalogue;
- define larger candidate thresholds and preference modes only after approved requirements.

### TD-013 — Equipment domain completion

Persist recipe equipment requirements, aggregate maximum simultaneous need, support manual overrides, and join equipment to transactional recalculation.

### TD-014 — Export templates and branding

Complete Russian PDF/Excel templates and load club logo and name from settings.

### TD-015 — Audit log

Record actor/action/time metadata when multi-user access is introduced.

### TD-019 — Dish recipe change impact preview

Show how many existing plans and purchasing projections will be recalculated before recipe replacement.

### TD-020 — Centralized product-policy validation

Apply approved product restrictions consistently in backend product, recipe, dish, and import validation with regression tests.

### TD-025 — Complete Product CRUD

Product currently supports list and create. Update and guarded delete remain unimplemented.

### TD-026 — Shopping and packaging review

Merged PR #70 delivers:

- project checklist product names;
- required, purchased, and non-negative remaining quantities;
- purchased-quantity validation;
- editable checked state and quantities;
- progress and responsive browser coverage.

Draft PR #71 delivers:

- PurchaseList product names;
- total purchase quantity derived from persisted package size and count;
- non-negative package surplus;
- package size, package count, purchase quantity, and surplus presentation;
- backend API, frontend helper, and browser coverage.

Required after PR #71:

- add optional responsible-person text;
- integrate shopping review into complete guided-preparation acceptance;
- verify recalculation changes remain visible without losing user purchase progress.

## Completed history

- TD-001 — accidental public API placeholders removed.
- TD-003 — participant, MealSlot, and Dish recipe purchasing refresh implemented transactionally.
- TD-004 — local stack and primary workflow verified during stabilization.
- TD-009 — dependency audit passes at moderate severity.
- TD-016 — backup/restore scripts and CI smoke test implemented.
- TD-017 — Meal Plan Editor UX and responsive browser acceptance completed.
- TD-018 — dish catalogue and active-recipe assignment implemented.
- TD-021 — MealSlot relation identifiers and frontend contract repaired.
- TD-022 — invalid selection-count pseudo cooldown removed.
- TD-023 — backend meal-boundary authority and regressions delivered.
