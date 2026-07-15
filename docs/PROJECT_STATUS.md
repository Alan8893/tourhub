# TourHub Project Status

Status date: 2026-07-15

## Current phase

Critical stabilization of the single-club preparation workflow. New menu-intelligence features remain paused until TH-0070 is merged and verified.

## Verified baseline before TH-0070

- Alembic has one head: `g10001`.
- Backend tests, selected Ruff and strict mypy baselines, frontend tests/build/audit, and PostgreSQL backup/restore are enforced in GitHub Actions.
- Docker Compose, automatic migrations, project creation, menu generation, preparation, and export foundations were verified during the stabilization cycle.
- Recipe library, dish catalogue, project catalogue, CSV import, and purchasing recalculation are present in `main`.

## TH-0070 stabilization scope

The current stabilization branch repairs the following audited regressions:

- MealSlot frontend consumes the real `/dishes` response envelope;
- MealPlan API exposes `MealSlotDish.id` and frontend mutations use it;
- API mapping no longer duplicates legacy MealPlanItem data when MealSlots exist;
- meal ordering is `breakfast`, `snack`, `lunch`, `dinner` in the frontend;
- project meal-boundary validation is enforced in Backend;
- dishes with archived recipes cannot be assigned to MealSlots;
- generation warnings are returned from project generation;
- unsupported standalone meal-plan placeholders are removed;
- the invalid selection-based pseudo three-day cooldown is removed;
- menu policy and generator join selected Ruff and strict mypy coverage.

These changes are not considered delivered in `main` until PR #54 is merged and its Quality workflow succeeds.

## Implemented product areas

### Projects

Implemented:

- project creation and preparation context;
- participant count and trip duration;
- first and last meal context;
- project catalogue and workspace;
- participant-count purchasing recalculation with rollback.

Needs completion:

- complete Russian guided workflow;
- equipment-dependent recalculation;
- invitation-only access after single-user acceptance.

### Meal plan

Implemented in `main`:

- persistent MealPlan, MealPlanDay, MealSlot, and MealSlotDish;
- multiple dishes per meal;
- add, remove, and replace backend operations;
- first/last meal schedule and one-day support;
- deterministic same-day uniqueness;
- deterministic fallback with insufficient-catalogue warning generation;
- purchasing recalculation and rollback after MealSlot edits;
- legacy MealPlanItem compatibility.

Pending TH-0070 merge:

- corrected frontend/backend MealSlot identifier contract;
- visible generation warning in the immediate project generation response;
- backend archived-recipe validation for MealSlot assignment;
- removal of duplicate flat API items and placeholder endpoints.

Needs later completion:

- persisted meal roles;
- breakfast/snack/lunch/dinner composition rules;
- repeatable drink/addition exceptions;
- calendar-day three-day main-dish diversity;
- warning persistence or deterministic reconstruction for later GET responses;
- responsive Meal Plan Editor UX.

### Dishes and recipes

Implemented:

- Dish and Recipe separation;
- dish catalogue and editor;
- explicit active-recipe assignment;
- archived-recipe historical visibility;
- recipe library and editor;
- RecipeComponent CRUD and quantity modes;
- product reading and creation;
- recipe notes;
- archive, restore, and guarded deletion;
- transactional CSV import;
- purchasing recalculation after Dish recipe replacement.

Needs completion:

- impact preview before recipe replacement;
- product update/delete;
- preparation, equipment, dietary, season, and category metadata;
- alcohol prohibition enforcement;
- multiple recipe variants and ownership after multi-user mode.

### Shopping and documents

Implemented:

- ingredient aggregation;
- shopping list and purchase checklist;
- package rounding foundation;
- transactional recalculation after participant, MealSlot, and Dish recipe changes;
- checklist state preservation;
- PDF/Excel/package export foundations;
- PostgreSQL backup/restore scripts and CI smoke test.

Needs completion:

- complete package and remainder presentation;
- responsible-person field;
- equipment pipeline;
- final Russian templates and club branding.

## Quality status

Enforced:

- backend tests;
- critical Ruff baseline;
- selected expanded Ruff baseline;
- selected strict mypy baseline;
- Alembic single-head validation;
- frontend Node tests;
- dependency audit at moderate severity;
- TypeScript production build;
- PostgreSQL backup/restore smoke test.

Open quality debt:

- confirm PR #54 Quality result;
- broader Ruff and strict mypy coverage;
- React component/API integration tests;
- responsive tests;
- Docker image/build and final release gates.

## Active tasks

- TH-0061 — guided project preparation journey;
- TH-0061.5 — Meal Composition Rules Engine;
- TH-0065 — Meal Plan Editor UX;
- TH-0070 — critical meal-plan contract stabilization.

## Immediate sequence

1. Merge and verify TH-0070.
2. Complete TH-0065 against the corrected contract.
3. Approve and persist meal-role metadata.
4. Implement role-aware composition and calendar-day diversity.
5. Complete packaging, equipment, exports, and release acceptance.
6. Introduce invitation-only access and roles.
