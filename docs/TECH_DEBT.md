# TourHub Technical Debt

Status date: 2026-07-15

Technical debt is prioritized by product risk.

## P0 — Release blockers

No open P0 release blockers are recorded after TH-0070 / PR #54.

## P1 — Quality and maintainability

### TD-005 — Ruff backlog

The audited snapshot contained 195 Ruff violations. A critical baseline and selected workflow baseline are enforced. Continue expanding coverage without increasing debt.

### TD-006 — Strict mypy backlog

The audited snapshot contained 74 strict mypy errors. Selected workflow modules, including the menu policy and generator, are clean and enforced.

### TD-007 — Frontend automated tests

Current coverage focuses on pure state, command, validation, ordering, summary, feedback, and responsive-policy helpers.

TH-0065 adds coverage for MealSlot add/replace/remove commands, mutation errors, Russian success feedback, day summaries, meal ordering, collapse defaults, and responsive layout policy.

Remaining critical coverage:

- browser-level React component and API integration for MealSlot editing;
- project creation and guided preparation;
- shopping recalculation presentation;
- catalogue import interaction and error rendering;
- responsive browser behavior at 360 px.

### TD-008 — Continuous Integration

Implemented gates include backend tests, selected Ruff/mypy, Alembic single-head, frontend tests/build/audit, and PostgreSQL backup/restore.

Remaining:

- Docker image/build validation;
- final release-acceptance workflow.

### TD-010 — Documentation and ADR consistency

Canonical current documents and the active task index are synchronized after TH-0070. Historical archive documents and duplicate ADR-011 history still require explicit canonical labelling where ambiguity remains.

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

Remaining work:

- persisted meal-role metadata;
- role composition for breakfast, snack, lunch, and dinner;
- approved repeatable roles;
- calendar-day three-day main-dish diversity;
- manual-selection preservation;
- warning persistence or reconstruction;
- preference modes after multi-variant recipes.

Same-day uniqueness and immediate generation warning fallback are implemented and are no longer open parts of TD-012.

### TD-013 — Equipment domain completion

Persist recipe equipment requirements, aggregate maximum simultaneous need, support manual overrides, and join equipment to transactional recalculation.

### TD-014 — Export templates and branding

Complete Russian PDF/Excel templates and load club logo and name from settings.

### TD-015 — Audit log

Record actor/action/time metadata when multi-user access is introduced.

### TD-017 — Meal plan editor UX

TH-0065 currently covers compact Russian rows, domain meal order, collapsible days, explicit add/replace flows, confirmed removal, mutation feedback, full-width layout, and responsive Material UI direction.

Remaining closure requirements:

- browser-level React/API integration tests;
- verified 360 px browser rendering;
- final desktop, tablet, and mobile acceptance.

### TD-019 — Dish recipe change impact preview

Show how many existing plans and purchasing projections will be recalculated before recipe replacement.

### TD-020 — Alcohol prohibition enforcement

Apply the prohibition consistently in backend product, recipe, dish, and import validation with regression tests.

### TD-025 — Complete Product CRUD

Product currently supports list and create. Update and guarded delete remain unimplemented.

## Completed history

- TD-001 — accidental public API placeholders removed.
- TD-003 — participant, MealSlot, and Dish recipe purchasing refresh implemented transactionally.
- TD-004 — local stack and primary workflow verified during stabilization.
- TD-009 — dependency audit passes at moderate severity.
- TD-016 — backup/restore scripts and CI smoke test implemented.
- TD-018 — dish catalogue and active-recipe assignment implemented.
- TD-021 — MealSlot relation identifiers and `/dishes` frontend contract repaired by PR #54.
- TD-022 — invalid selection-count pseudo cooldown removed by PR #54.
- TD-023 — backend meal-boundary authority and regression tests delivered by PR #54.
