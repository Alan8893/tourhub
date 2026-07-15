# TourHub Technical Debt

Status date: 2026-07-15

Technical debt is prioritized by product risk.

## P0 — Release blockers

### TD-021 — MealSlot API contract regression

Status: IN REVIEW in TH-0070 / PR #54.

The API previously omitted `MealSlotDish.id`, while frontend replace/remove mutations sent `dish_id`. The MealSlot dish selector also treated the `/dishes` envelope as a raw array.

Closure requires:

- relation identifiers in the API;
- frontend use of relation identifiers;
- correct dish-list envelope handling;
- API and frontend regression coverage;
- successful Quality workflow.

### TD-022 — Invalid menu cooldown claim

Status: IN REVIEW in TH-0070 / PR #54.

The merged policy treated the last three selected dishes as a three-day cooldown and defaulted every DishInput to a main dish. This is not the approved calendar-day, role-aware rule.

Closure requires removal of the invalid behavior and documentation that three-day diversity remains unimplemented until persisted meal roles are approved.

### TD-023 — Backend meal-boundary authority

Status: IN REVIEW in TH-0070 / PR #54.

Project creation previously relied on frontend-only one-day validation and accepted unknown meal strings through the API.

Closure requires backend validation and regression tests.

## P1 — Quality and maintainability

### TD-005 — Ruff backlog

The audited snapshot contained 195 Ruff violations. A critical baseline and selected workflow baseline are enforced. Continue expanding coverage without increasing debt.

### TD-006 — Strict mypy backlog

The audited snapshot contained 74 strict mypy errors. Selected workflow modules are clean and enforced. TH-0070 adds the menu policy and generator to the typed baseline.

### TD-007 — Frontend automated tests

Current coverage focuses on pure state and validation helpers. Remaining critical coverage:

- React component and API integration for MealSlot editing;
- project creation and guided preparation;
- shopping recalculation presentation;
- catalogue import interaction and error rendering;
- responsive behavior.

### TD-008 — Continuous Integration

Implemented gates include backend tests, selected Ruff/mypy, Alembic single-head, frontend tests/build/audit, and PostgreSQL backup/restore.

Remaining:

- Docker image/build validation;
- final release-acceptance workflow.

### TD-010 — Documentation and ADR consistency

TH-0070 synchronizes canonical current documents and removes the duplicate active TH-0061.5 task file. Historical archive documents and duplicate ADR-011 history still require explicit canonical labelling where ambiguity remains.

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

Complete Russian labels, compact rows, domain meal order, responsive editing, collapsible days, mutation feedback, confirmation/undo affordances, and responsive tests.

### TD-019 — Dish recipe change impact preview

Show how many existing plans and purchasing projections will be recalculated before recipe replacement.

### TD-020 — Alcohol prohibition enforcement

Apply the prohibition consistently in backend product, recipe, dish, and import validation with regression tests.

### TD-025 — Complete Product CRUD

Product currently supports list and create. Update and guarded delete remain unimplemented.

## Completed history

- TD-001 — accidental public API placeholders removed; TH-0070 removes the remaining unused legacy router and standalone fake response.
- TD-003 — participant, MealSlot, and Dish recipe purchasing refresh implemented transactionally.
- TD-004 — local stack and primary workflow verified during stabilization.
- TD-009 — dependency audit passes at moderate severity.
- TD-016 — backup/restore scripts and CI smoke test implemented.
- TD-018 — dish catalogue and active-recipe assignment implemented.
