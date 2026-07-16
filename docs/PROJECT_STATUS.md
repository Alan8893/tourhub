# TourHub Project Status

Status date: 2026-07-16

## Current phase

TH-0061.5 — persisted Dish classification, the Russian catalogue editor, deterministic readiness warnings, and required role-aware generation are implemented through PRs #59–#63. Automatic generation now uses both Dish role and compatible meal type. The active deployment catalogue still requires explicit classification, while optional additions/drinks, calendar-day diversity, and manual-choice preservation remain later slices.

## Verified baseline

- TH-0070 was merged through PR #54.
- Remote-browser same-origin API routing was repaired through PR #56.
- TH-0065 Meal Plan Editor UX was completed through PR #55 and PR #57.
- Quality run #169 verified real-browser MealSlot mutations and responsive 1280, 768, and 360 px layouts before PR #57 merge.
- Alembic has one head: `h10001`.
- PRs #59, #60, and #61 merged persisted classification, its editor, and catalogue readiness into `main`.
- PR #62 repaired the real mobile navigation drawer reported from the LAN deployment.
- Quality run #240 verifies required role- and meal-type-aware generation on PR #63.
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
- optional addition/drink readiness recommendations;
- visible Russian readiness warnings refreshed after role edits;
- automatic selection filtered by both persisted role and current meal type;
- one compatible `main` generated for breakfast, lunch, and dinner;
- one compatible `snack` generated for the snack slot;
- unclassified and archived-recipe Dishes excluded from automatic selection;
- missing required pools persisted as empty MealSlots with explicit warnings;
- per-role `is_repeatable` respected during same-day required-role selection.

Needs later completion:

- explicit classification of the active deployment catalogue;
- optional `addition` and `drink` composition inside generated MealSlots;
- larger candidate thresholds for diversity;
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
- exclusion of archived-recipe dishes from readiness and generation candidates;
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
- responsive application-navigation real-browser acceptance;
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

Verified on PR #61 Quality run #234 after retargeting to `main`:

- stable readiness coverage order and thresholds;
- optional coverage does not block readiness;
- archived recipes are excluded from counts;
- Russian required/recommended warning presentation;
- readiness refresh after classification mutation;
- desktop and 360 px no-overflow screenshots;
- the readiness service is included in Ruff and strict mypy gates.

Verified on PR #63 Quality run #240:

- breakfast-only porridge cannot be selected for lunch or dinner;
- lunch/dinner-only borscht cannot be selected for breakfast;
- snack slots use only `snack` assignments;
- unclassified and archived-recipe Dishes are excluded;
- missing required pools create empty persisted MealSlots and warnings;
- repeatable assignments may be reused without an insufficient-catalogue warning;
- non-repeatable pool exhaustion remains deterministic and warns;
- MealSlotDish relation IDs remain distinct from Dish IDs;
- all existing frontend/browser, Alembic, and PostgreSQL gates remain green.

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

1. Merge PR #63 after review.
2. Classify the active deployment catalogue explicitly using roles and meal types.
3. Add optional repeatable `addition` and `drink` composition.
4. Implement calendar-day three-day main-dish diversity.
5. Preserve manual selections during regeneration and reconstruct warnings on later reads.
6. Complete packaging, equipment, exports, and release acceptance.
7. Introduce invitation-only access and roles.
