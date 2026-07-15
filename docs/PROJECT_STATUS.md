# TourHub Project Status

Status date: 2026-07-15

## Current phase

TH-0061.5 — persisted Dish roles and meal-type compatibility are implemented on PR #59, the Russian catalogue editor is implemented on PR #60, and deterministic catalogue readiness with visible Russian warnings is implemented on stacked PR #61. Role-aware generation remains deferred until the active deployment catalogue is classified and the selection policy is connected to this metadata.

## Verified baseline

- TH-0070 was merged through PR #54.
- Remote-browser same-origin API routing was repaired through PR #56.
- TH-0065 Meal Plan Editor UX was completed through PR #55 and PR #57.
- Quality run #169 verified real-browser MealSlot mutations and responsive 1280, 768, and 360 px layouts before PR #57 merge.
- Alembic has one head: `h10001` on PR #59.
- Quality run #197 verifies the persisted role/meal-type backend contract on PR #59.
- Quality run #206 verifies the stacked role editor and responsive browser acceptance on PR #60.
- Quality run #225 verifies the initial catalogue-readiness API, frontend warnings, and browser refresh flow on PR #61.
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
- normalized `dish_meal_roles` persistence;
- normalized `dish_meal_role_meal_types` compatibility;
- multiple roles per Dish, repeatability per role, and compatibility per role/meal type;
- atomic full classification replacement with no heuristic migration backfill;
- backend compatibility enforcement for breakfast, snack, lunch, and dinner;
- Russian catalogue editor for roles, meal types, and repeatability;
- deterministic minimum catalogue-readiness evaluation;
- required `main` pools for breakfast/lunch/dinner and required `snack` pool for snack;
- optional addition/drink recommendations;
- visible Russian readiness warnings refreshed after role edits.

Needs later completion:

- explicit classification of the active deployment catalogue;
- role- and meal-type-aware generation;
- larger candidate thresholds for diversity;
- repeatable drink/addition behavior in generation;
- calendar-day three-day main-dish diversity;
- manual-selection preservation during regeneration;
- generation-warning persistence or deterministic reconstruction for later GET responses.

### Dishes and recipes

Implemented:

- Dish and Recipe separation;
- dish catalogue and editor;
- explicit active-recipe assignment;
- archived-recipe historical visibility;
- persisted multi-role classification and per-role meal compatibility backend/API;
- Russian role/meal-type management UI with responsive browser coverage;
- active/classified/unclassified Dish readiness counts;
- exclusion of archived-recipe dishes from readiness candidates;
- recipe library and editor;
- RecipeComponent CRUD and quantity modes;
- product reading and creation;
- recipe notes;
- archive, restore, and guarded deletion;
- transactional CSV import;
- purchasing recalculation after Dish recipe replacement.

Needs completion:

- classification of the active deployment catalogue;
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
- Dish catalogue-readiness real-browser acceptance;
- desktop, tablet, and 360 px screenshot artifacts;
- PostgreSQL backup/restore smoke test.

Verified on PR #59 Quality run #197:

- normalized role and meal-type compatibility persistence;
- transactional classification replacement and clearing;
- duplicate role/type atomic rejection;
- empty, invalid, incompatible, and unknown-dish rejection;
- stable Dish list/detail response ordering;
- single Alembic head `h10001`.

Verified on PR #60 Quality run #206:

- role draft hydration and stable serialization;
- explicit meal-type selection requirement;
- exact classification PUT payload;
- success and injected backend error feedback;
- lunch-only main classification and repeatable drink classification;
- no horizontal overflow at 1280, 768, and 360 px.

Verified on PR #61 Quality run #225:

- stable readiness coverage order and thresholds;
- optional coverage does not block readiness;
- archived recipes are excluded from counts;
- Russian required/recommended warning presentation;
- readiness refresh after classification mutation;
- desktop and 360 px no-overflow screenshots;
- the new readiness service is included in Ruff and strict mypy gates.

Open quality debt:

- guided preparation browser coverage;
- active deployment catalogue acceptance data;
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
3. Retarget PR #61 to `main`, rerun Quality, and merge it.
4. Classify the active deployment catalogue explicitly using roles and meal types.
5. Implement role-aware composition and calendar-day diversity.
6. Complete packaging, equipment, exports, and release acceptance.
7. Introduce invitation-only access and roles.
