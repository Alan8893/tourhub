# TourHub Project Status

Status date: 2026-07-16

## Current phase

TH-0061.5 approved menu-rule implementation is complete in `main` through PR #69. The active product phase is TH-0061 guided preparation, starting with a usable Russian purchase checklist in draft PR #70.

Merged delivery chain:

- PR #59 — normalized Dish roles and role-specific meal-type compatibility;
- PR #60 — Russian catalogue editor for roles, meal types, and repeatability;
- PR #61 — deterministic catalogue-readiness API and visible Russian warnings;
- PR #62 — responsive mobile navigation drawer;
- PR #64 — role- and meal-type-aware project meal-plan generation;
- PR #65 — canonical documentation synchronization;
- PR #66 — calendar-day three-day diversity for `main` dishes;
- PR #67 — authoritative preservation of manually edited MealSlots during regeneration;
- PR #69 — persisted generation-warning lifecycle.

Open implementation:

- draft PR #70 — editable project purchase checklist with required, purchased, and remaining quantities.

Automatic menu generation uses only explicitly classified, active-recipe dishes. Manual choices remain available independently of automatic classification.

## Verified baseline

- Current `main` includes PR #69 at squash commit `3a368203c1a1308bea736d799a0e1a6136cd11f2`.
- Alembic has one head: `h10003`.
- Exact-head Quality #271 passed before PR #66 merge.
- Exact-head Quality #273 passed before PR #67 merge.
- Exact-head Quality #280 passed before PR #69 merge with backend, frontend, Alembic, browser, and PostgreSQL gates green.
- MealSlot and MealSlotDish are the primary menu-composition persistence model.
- MealPlanItem remains a legacy compatibility path.
- Docker Compose, automatic migrations, LAN-safe same-origin routing, project creation, menu editing, purchasing recalculation, and export foundations are operational.

## Implemented product areas

### Projects

- project creation and catalogue;
- participant count, duration, first meal, and last meal;
- backend meal-boundary validation;
- project workspace routing;
- participant-count purchasing recalculation with rollback;
- same-origin browser routing for LAN clients.

Still required:

- complete the guided Russian preparation workflow;
- equipment-dependent recalculation;
- invitation-only access after single-user acceptance.

### Meal plan

- persisted MealPlan, MealPlanDay, MealSlot, and MealSlotDish;
- first/last meal scheduling and one-day support;
- multiple dishes per MealSlot;
- add, replace, and remove operations;
- corrected MealSlotDish identifier contract;
- compact responsive Russian editor;
- normalized Dish role and meal-type compatibility;
- catalogue-readiness evaluation and visible warnings;
- automatic filtering by persisted role and meal type;
- required `main` for breakfast/lunch/dinner and required `snack` for snack;
- optional compatible `addition` and `drink` selection;
- stable composition order `main → addition → drink`;
- repeatability evaluated per `(dish, role)` assignment;
- same-day uniqueness and calendar-day three-day `main` diversity;
- day-four reuse and repeatable-main bypass;
- archived-recipe and unclassified dishes excluded from automatic generation;
- explicit required-pool warnings instead of hidden incompatible fallback;
- generated compositions persisted through MealSlot/MealSlotDish and compatibility MealPlanItem rows;
- explicit `MealSlot.is_manually_edited` marker through Alembic revision `h10002`;
- preservation of non-empty and empty manual slots during regeneration;
- reuse of one project MealPlan instead of duplicate-plan creation;
- persisted ordered warning snapshot through Alembic revision `h10003`;
- identical warnings on generation and later GET responses;
- warning replacement and clearing on regeneration;
- transactional purchasing recalculation after MealSlot edits.

Operational follow-up:

- maintain explicit classification of the active deployment catalogue;
- add larger thresholds or preference modes only after approved requirements.

### Dishes and recipes

- Dish and Recipe separation;
- dish catalogue, create, rename, and active-recipe assignment;
- persisted multi-role classification with per-role meal compatibility and repeatability;
- atomic classification replacement API;
- Russian role/meal-type editor;
- active/classified/unclassified readiness counts;
- archived-recipe exclusion from readiness and automatic generation candidates;
- recipe components, quantity modes, notes, archive/restore, and guarded deletion;
- transactional CSV import;
- purchasing recalculation after Dish recipe replacement.

Still required:

- impact preview before recipe replacement;
- product update/delete;
- preparation, equipment, dietary, season, and category metadata;
- centralized alcohol-prohibition enforcement;
- multiple recipe variants and ownership after multi-user mode.

### Shopping and documents

Implemented:

- ingredient aggregation;
- purchase list and purchase checklist persistence;
- package-rounding foundation;
- purchased-quantity and checked-state persistence;
- transactional recalculation after participant, MealSlot, and Dish recipe changes;
- checklist-state preservation;
- PDF/Excel/package export foundations;
- PostgreSQL backup/restore scripts and CI smoke test.

Draft PR #70 adds:

- product names in checklist API responses;
- non-negative computed remaining quantities;
- validation against negative purchased quantities;
- editable Russian checklist inside the project workspace;
- required, purchased, and remaining quantity presentation;
- completion progress, loading/error/success feedback, and responsive layout;
- backend API, frontend state, and browser acceptance coverage.

Still required after PR #70:

- package-count and package-surplus review presentation;
- optional responsible-person text;
- equipment pipeline;
- final Russian templates and club branding.

## Quality status

Enforced gates:

- backend tests;
- critical and selected expanded Ruff baselines;
- selected strict mypy baseline;
- Alembic single-head validation;
- frontend Node tests and dependency audit;
- TypeScript production build;
- Meal Plan Editor browser acceptance;
- Dish role/meal-compatibility browser acceptance;
- catalogue-readiness browser acceptance;
- responsive application navigation browser acceptance;
- desktop, tablet, and 360 px no-overflow checks and screenshots;
- PostgreSQL backup/restore smoke test.

Draft PR #70 extends this with purchase-checklist browser acceptance for quantity editing, remainder refresh, checked-state updates, and 360 px overflow protection.

Open quality debt:

- complete guided preparation browser coverage;
- active deployment catalogue acceptance data;
- package review and recalculation presentation;
- catalogue import interaction and error rendering;
- explicit PostgreSQL migration upgrade/downgrade smoke;
- Docker image/build CI validation;
- final release-acceptance workflow.

## Active tasks

- TH-0061 — guided project preparation journey and purchase workflow;
- TH-0061.5 — operational catalogue maintenance only; approved rules implementation is complete.

## Immediate sequence

1. Complete exact-head Quality and review for draft PR #70.
2. Add package-count/surplus review and optional responsible-person text.
3. Implement equipment requirements, aggregation, overrides, and recalculation.
4. Complete final Russian documents and end-to-end release acceptance.
5. Introduce invitation-only access and roles only after single-user acceptance.
