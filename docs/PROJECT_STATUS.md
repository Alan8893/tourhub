# TourHub Project Status

Status date: 2026-07-15

## Current phase

TH-0061.5 — implement the persisted Dish meal-role metadata approved by ADR-013. Role-aware generation remains deferred until the schema, API, catalogue classification workflow, and readiness validation are complete.

## Verified baseline

- TH-0070 was merged through PR #54.
- Remote-browser same-origin API routing was repaired through PR #56.
- TH-0065 Meal Plan Editor UX was completed through PR #55 and PR #57.
- Quality run #169 verified real-browser MealSlot mutations and responsive 1280, 768, and 360 px layouts before PR #57 merge.
- Alembic has one head: `g10001`.
- Backend tests, selected Ruff and strict mypy baselines, frontend tests/build/audit/browser acceptance, and PostgreSQL backup/restore are enforced in GitHub Actions.
- Docker Compose, automatic migrations, project creation, menu generation, preparation, and export foundations were verified during stabilization.
- Recipe library, dish catalogue, project catalogue, CSV import, and purchasing recalculation are present in `main`.
- MealSlot API exposes persisted relation identifiers and frontend mutations use them.
- Backend validates project meal boundaries and blocks assignment of dishes with archived recipes.
- Immediate generation warnings are returned to the frontend.
- Unsupported meal-plan placeholders and the invalid selection-based pseudo three-day cooldown are removed.

## Implemented product areas

### Projects

Implemented:

- project creation and preparation context;
- participant count and trip duration;
- first and last meal context;
- backend boundary validation;
- project catalogue and workspace;
- participant-count purchasing recalculation with rollback;
- same-origin browser routing for LAN clients.

Needs completion:

- complete Russian guided workflow;
- equipment-dependent recalculation;
- invitation-only access after single-user acceptance.

### Meal plan

Implemented in `main`:

- persistent MealPlan, MealPlanDay, MealSlot, and MealSlotDish;
- multiple dishes per meal;
- add, remove, and replace backend operations;
- corrected frontend/backend MealSlot identifier contract;
- first/last meal schedule and one-day support;
- deterministic same-day uniqueness;
- deterministic fallback with immediate insufficient-catalogue warning generation;
- archived-recipe assignment guard;
- purchasing recalculation and rollback after MealSlot edits;
- legacy MealPlanItem compatibility without duplicate flat API items;
- compact Russian editor rows;
- explicit replace/add flows and confirmed removal;
- mutation loading, success, and error feedback;
- collapsible days with dish counts;
- full-width responsive editor layout;
- browser-level add, replace, remove, confirmation, error, and responsive acceptance.

Approved but not implemented:

- ADR-013 normalized `dish_meal_roles` model;
- roles `main`, `addition`, `drink`, and `snack`;
- multiple roles per Dish;
- repeatability per `(dish, role)` assignment;
- atomic role replacement API contract;
- migration without heuristic role inference.

Needs later completion:

- `DishMealRoleORM`, migration, repository, service, schemas, and API;
- catalogue role management UI and explicit catalogue classification;
- readiness validation and warnings;
- breakfast/snack/lunch/dinner composition rules;
- repeatable drink/addition exceptions;
- calendar-day three-day main-dish diversity;
- manual-selection preservation during regeneration;
- warning persistence or deterministic reconstruction for later GET responses.

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

- meal-role persistence and role-management UI;
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

Enforced in `main`:

- backend tests;
- critical Ruff baseline;
- selected expanded Ruff baseline;
- selected strict mypy baseline;
- Alembic single-head validation;
- frontend Node tests;
- dependency audit at moderate severity;
- TypeScript production build;
- Meal Plan Editor real-browser acceptance and screenshot artifacts;
- PostgreSQL backup/restore smoke test.

Open quality debt:

- guided preparation browser coverage;
- shopping and catalogue-import browser coverage;
- meal-role migration and API integration coverage;
- broader Ruff and strict mypy coverage;
- Docker image/build and final release gates.

## Active tasks

- TH-0061 — guided project preparation journey;
- TH-0061.5 — Meal Composition Rules Engine.

## Immediate sequence

1. Implement `dish_meal_roles` persistence and Alembic migration.
2. Implement role schemas, service, repository, and atomic API contract.
3. Add dish-editor role management and browser/API tests.
4. Classify the active catalogue explicitly and validate readiness.
5. Implement role-aware composition and calendar-day diversity.
6. Complete packaging, equipment, exports, and release acceptance.
7. Introduce invitation-only access and roles.