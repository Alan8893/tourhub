# TourHub Project Status

Status date: 2026-07-16

## Current phase

TH-0061.5 remains active only for generation-warning persistence. Persisted classification, role-aware generation, calendar-day `main` diversity, and manual-slot preservation are merged in `main`.

Merged delivery chain:

- PR #59 — normalized Dish roles and role-specific meal-type compatibility;
- PR #60 — Russian catalogue editor for roles, meal types, and repeatability;
- PR #61 — deterministic catalogue-readiness API and visible Russian warnings;
- PR #62 — responsive mobile navigation drawer;
- PR #64 — role- and meal-type-aware project meal-plan generation;
- PR #65 — canonical documentation synchronization;
- PR #66 — calendar-day three-day diversity for `main` dishes;
- PR #67 — authoritative preservation of manually edited MealSlots during regeneration.

Open implementation:

- draft PR #69 — persistence of the latest generation-warning snapshot for later GET responses.

The Product Owner verified the deployed role-aware generation after PR #64. Automatic generation uses only explicitly classified, active-recipe dishes, while manual choices remain available independently of automatic classification.

## Verified baseline

- Current `main` includes PR #67 at squash commit `10e4756c4bfc6f45414c0afcb297ad149f6e4b8b`.
- Alembic has one head: `h10002`; draft PR #69 adds `h10003`.
- Exact-head Quality #271 passed before PR #66 merge.
- Exact-head Quality #273 passed before PR #67 merge with backend, frontend, Alembic, browser, and PostgreSQL gates green.
- MealSlot and MealSlotDish are the primary menu-composition persistence model.
- MealPlanItem remains a legacy compatibility path.
- MealSlot API responses expose persisted relation identifiers separately from source `dish_id` values.
- Docker Compose, automatic migrations, LAN-safe same-origin routing, mobile navigation, project creation, menu editing, purchasing recalculation, and export foundations are operational.

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
- automatic filtering by both persisted role and current meal type;
- required `main` for breakfast/lunch/dinner and required `snack` for snack;
- optional compatible `addition` and `drink` selection;
- stable composition order `main → addition → drink`;
- repeatability evaluated per `(dish, role)` assignment;
- same-day uniqueness for non-repeatable assignments;
- trip-calendar-day three-day diversity for non-repeatable `main` assignments;
- day-four reuse and repeatable-main bypass;
- archived-recipe and unclassified dishes excluded from automatic generation;
- explicit required-pool warnings instead of hidden incompatible fallback;
- generated compositions persisted through MealSlot/MealSlotDish and compatibility MealPlanItem rows;
- explicit `MealSlot.is_manually_edited` marker through Alembic revision `h10002`;
- manual add, replace, and remove marking the complete slot as authoritative;
- preservation of non-empty and empty manual slots during regeneration;
- reuse of one project MealPlan instead of duplicate-plan creation;
- no role inference for unclassified manual dishes;
- transactional purchasing recalculation after MealSlot edits.

Draft PR #69 adds:

- an ordered persisted `MealPlan.warnings` snapshot through Alembic revision `h10003`;
- the same warnings in POST generation and later GET responses;
- snapshot stability when catalogue data changes without regeneration;
- atomic replacement and clearing on the next regeneration;
- public API lifecycle regression coverage.

Still required for TH-0061.5 after PR #69:

- maintain and complete explicit classification of the active deployment catalogue;
- larger diversity thresholds and preference modes only after approved product requirements.

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

- ingredient aggregation;
- shopping list and purchase checklist;
- package-rounding foundation;
- transactional recalculation after participant, MealSlot, and Dish recipe changes;
- checklist-state preservation;
- PDF/Excel/package export foundations;
- PostgreSQL backup/restore scripts and CI smoke test.

Still required:

- complete package and remainder presentation;
- responsible-person field;
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

PR #66 regression scope verifies calendar-day diversity, repeatable-main bypass, pool exhaustion, service mapping, persistence alignment, and public API behavior.

PR #67 regression scope verifies manual mutation marking, authoritative non-empty and empty slots, no role inference, one-plan reuse, subsequent GET persistence, and unchanged generation of unmarked slots.

PR #69 regression scope verifies persisted warning order, later GET behavior, stability across catalogue-only changes, and replacement after regeneration.

Open quality debt:

- guided preparation browser coverage;
- active deployment catalogue acceptance data;
- shopping and catalogue-import browser coverage;
- explicit PostgreSQL migration upgrade/downgrade smoke;
- Docker image/build CI validation;
- final release-acceptance workflow.

## Active tasks

- TH-0061 — guided project preparation journey;
- TH-0061.5 — complete generation-warning lifecycle, then maintain real catalogue data.

## Immediate sequence

1. Complete exact-head Quality and review for draft PR #69.
2. Keep the active catalogue explicitly classified and verify readiness on real deployment data.
3. Complete the guided preparation, packaging, equipment, and export acceptance workflow.
4. Introduce invitation-only access and roles only after single-user acceptance.
