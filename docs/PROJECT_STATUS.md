# TourHub Project Status

Status date: 2026-07-15

## Current phase

TH-0065 — Meal Plan Editor UX is ready for Product Owner review on PR #57. New menu-intelligence metadata and rules remain deferred until this editor workflow is accepted and merged.

## Verified baseline

- TH-0070 was merged through PR #54.
- Remote-browser same-origin API routing was repaired through PR #56.
- Alembic has one head: `g10001`.
- Backend tests, selected Ruff and strict mypy baselines, frontend tests/build/audit, and PostgreSQL backup/restore are enforced in GitHub Actions.
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
- full-width responsive editor layout.

Pending PR #57 merge:

- browser-level React/API acceptance for add, replace, remove, and mutation errors;
- automated no-overflow checks at 1280, 768, and 360 px;
- desktop, tablet, and mobile screenshot artifacts in Quality CI.

Needs later completion:

- persisted meal roles;
- breakfast/snack/lunch/dinner composition rules;
- repeatable drink/addition exceptions;
- calendar-day three-day main-dish diversity;
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
- PostgreSQL backup/restore smoke test.

Verified on PR #57 Quality run #164:

- real-browser MealSlot add, replace, remove, confirmation, and error flows;
- same-origin Vite proxy integration against a mock API;
- responsive no-overflow checks and screenshots at desktop, tablet, and 360 px mobile widths.

Open quality debt:

- guided preparation browser coverage;
- shopping and catalogue-import browser coverage;
- broader Ruff and strict mypy coverage;
- Docker image/build and final release gates.

## Active tasks

- TH-0061 — guided project preparation journey;
- TH-0061.5 — Meal Composition Rules Engine;
- TH-0065 — Meal Plan Editor UX, ready for review on PR #57.

## Immediate sequence

1. Complete Product Owner review and merge PR #57.
2. Close TH-0065 after merge verification.
3. Approve and persist meal-role metadata.
4. Implement role-aware composition and calendar-day diversity.
5. Complete packaging, equipment, exports, and release acceptance.
6. Introduce invitation-only access and roles.
