# TourHub Project Status

Status date: 2026-07-15

## Current phase

TH-0061.5 — persisted Dish roles and per-role meal-type compatibility are implemented on PR #59, while the Russian catalogue editor and real-browser acceptance are implemented on stacked PR #60. The next slice is explicit active-catalogue classification and deterministic readiness validation. Role-aware generation remains deferred until those data and warning paths are complete.

## Verified baseline

- TH-0070 was merged through PR #54.
- Remote-browser same-origin API routing was repaired through PR #56.
- TH-0065 Meal Plan Editor UX was completed through PR #55 and PR #57.
- Quality run #169 verified real-browser MealSlot mutations and responsive 1280, 768, and 360 px layouts before PR #57 merge.
- Alembic has one head: `h10001` on PR #59.
- Quality run #197 verifies the persisted role/meal-type backend contract on PR #59.
- Quality run #206 verifies the stacked role editor, exact API payload, local validation, backend error rendering, and responsive layouts on PR #60.
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

Implemented:

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
- browser-level add, replace, remove, confirmation, error, and responsive acceptance;
- normalized `dish_meal_roles` persistence with roles `main`, `addition`, `drink`, and `snack`;
- normalized `dish_meal_role_meal_types` compatibility for `breakfast`, `snack`, `lunch`, and `dinner`;
- multiple roles per Dish, repeatability per `(dish, role)`, and compatibility per `(dish, role, meal_type)`;
- atomic full classification replacement with no heuristic migration backfill;
- backend enforcement that `snack` is snack-only while `main`, `addition`, and `drink` use explicit breakfast/lunch/dinner compatibility;
- Russian catalogue editor for roles, meal types, and repeatability;
- browser/API acceptance proving lunch-only soup and multi-meal repeatable drink classification.

Needs later completion:

- explicit active-catalogue classification;
- catalogue readiness validation by meal type and visible warnings;
- breakfast/snack/lunch/dinner composition rules;
- repeatable drink/addition behavior in generation;
- calendar-day three-day main-dish diversity;
- manual-selection preservation during regeneration;
- warning persistence or deterministic reconstruction for later GET responses.

### Dishes and recipes

Implemented:

- Dish and Recipe separation;
- dish catalogue and editor;
- explicit active-recipe assignment;
- archived-recipe historical visibility;
- persisted multi-role classification and per-role meal compatibility backend/API;
- Russian role/meal-type management UI with responsive browser coverage;
- recipe library and editor;
- RecipeComponent CRUD and quantity modes;
- product reading and creation;
- recipe notes;
- archive, restore, and guarded deletion;
- transactional CSV import;
- purchasing recalculation after Dish recipe replacement.

Needs completion:

- explicit classification of the active catalogue;
- readiness evaluation and warnings;
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
- Meal Plan Editor real-browser acceptance;
- Dish role/meal-compatibility real-browser acceptance;
- desktop, tablet, and 360 px screenshot artifacts;
- PostgreSQL backup/restore smoke test.

Verified on PR #59 Quality run #197:

- normalized role and meal-type compatibility persistence;
- transactional classification replacement and clearing;
- duplicate role/type atomic rejection;
- empty, invalid, incompatible, and unknown-dish rejection;
- stable Dish list/detail response ordering;
- single Alembic head `h10001`;
- unchanged existing frontend/browser and PostgreSQL backup/restore gates.

Verified on PR #60 Quality run #206:

- role draft hydration and stable serialization;
- explicit meal-type selection requirement;
- exact `PUT /api/v1/dishes/{dish_id}/meal-roles` payload;
- success and injected backend error feedback;
- lunch-only `main` classification and breakfast/lunch/dinner repeatable drink classification;
- no horizontal overflow at 1280, 768, and 360 px;
- deterministic Chrome profile cleanup.

Open quality debt:

- guided preparation browser coverage;
- catalogue readiness and active-catalogue data coverage;
- shopping and catalogue-import browser coverage;
- explicit PostgreSQL migration upgrade smoke beyond single-head validation;
- broader Ruff and strict mypy coverage;
- Docker image/build and final release gates.

## Active tasks

- TH-0061 — guided project preparation journey;
- TH-0061.5 — Meal Composition Rules Engine.

## Immediate sequence

1. Merge PR #59.
2. Retarget PR #60 to `main`, rerun Quality, and merge it.
3. Classify the active catalogue explicitly using roles and meal types.
4. Add deterministic catalogue readiness validation and visible Russian warnings.
5. Implement role-aware composition and calendar-day diversity.
6. Complete packaging, equipment, exports, and release acceptance.
7. Introduce invitation-only access and roles.
