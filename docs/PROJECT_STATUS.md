# TourHub Project Status

Status date: 2026-07-15

## Current Phase

Single-club product completion. Multi-user access and administration are intentionally deferred while menu intelligence, shopping/equipment completeness, exports, and final UX acceptance are completed.

## Verified Baseline

- Alembic has one head: `g10001`.
- Backend functional tests pass in GitHub Actions.
- Selected Ruff and strict mypy baselines are enforced in GitHub Actions.
- Frontend state tests, moderate-severity dependency audit, TypeScript check, and production build pass in GitHub Actions.
- PostgreSQL 18 backup and restore are smoke-tested in GitHub Actions.
- MealSlot and dish recipe replacement operations trigger transactional purchasing recalculation.
- Full local stack startup, automatic migrations, project creation, menu generation, preparation, and exports were verified during the stabilization cycle.

## Implemented Product Areas

### Project workflow

Implemented:

- project creation and preparation context;
- participant count and trip duration;
- meal boundary context;
- project catalogue with navigation to individual workspaces;
- workspace preparation flow;
- participant-count purchasing recalculation with transactional rollback.

Needs completion:

- finalized Russian adaptive UX;
- fully guided preparation journey through final exports;
- equipment-dependent recalculation after the equipment domain is implemented;
- invitation-only authorization after the single-user MVP workflow is complete.

### Meal plan

Implemented:

- persistent MealPlan domain;
- days and meal schedule;
- MealSlot composition;
- multiple dishes per meal;
- add, remove, and replace dish operations;
- frontend MealSlot editor;
- purchasing recalculation after MealSlot edits;
- commit/rollback regression coverage;
- frontend loading, error, empty, ready, add, replace, remove, pending, and mutation-error state tests;
- legacy MealPlanItem compatibility.

Needs completion:

- approved meal composition and diversity rules;
- insufficient-catalogue warnings;
- responsive and higher-level interaction tests;
- TH-0065 Meal Plan Editor UX acceptance.

### Dishes and recipes

Implemented:

- Dish and Recipe separation foundation;
- dish catalogue API and frontend;
- dish creation, renaming, and explicit active-recipe assignment;
- recipe replacement with transactional recalculation of affected purchase lists and checklists;
- historical visibility for dishes whose assigned recipe is archived later;
- prevention of new archived-recipe assignment;
- complete single-club recipe library API and frontend;
- recipe creation and renaming;
- RecipeComponent CRUD;
- component roles and practical quantity calculation modes;
- product catalogue reading and creation;
- recipe note CRUD and priority ordering;
- active and archived library views;
- safe archive and restore;
- guarded physical deletion when a recipe is referenced by a dish;
- read-only archived recipe detail;
- transactional CSV preview/import for products, recipes, components, and notes;
- shopping integration with legacy fallback;
- regression coverage for read, write, validation, archive, restore, delete, import, assignment, and recalculation flows.

Current persistence stores one selected recipe per Dish. Multiple recipe variants and recipe preference modes remain target-domain work.

Needs completion:

- impact preview before replacing a recipe used by existing projects;
- preparation technology, equipment, dietary, season, and category metadata;
- alcohol prohibition validation across API and import;
- multiple recipe variants, ownership, publication, and moderation after multi-user mode is introduced.

### Shopping and documents

Implemented:

- ingredient aggregation;
- shopping list;
- purchase checklist;
- package rounding foundation;
- recalculation after participant, MealSlot, and Dish recipe changes;
- preservation of checklist state where products remain after recalculation;
- PDF, Excel, and package export foundations;
- PostgreSQL backup and restore scripts and operational documentation.

Needs completion:

- complete package/remainder presentation;
- equipment pipeline;
- final Russian templates with logo from settings.

## Quality Status

Passing and enforced:

- backend tests;
- selected Ruff baseline;
- selected strict mypy baseline;
- Alembic single-head validation;
- frontend automated tests;
- moderate-severity dependency audit;
- frontend TypeScript and production build;
- PostgreSQL backup/restore smoke test.

Open quality debt:

- broader Ruff cleanup;
- broader strict mypy cleanup;
- higher-level and responsive frontend tests;
- Docker image/build and final release-acceptance gates.

## Documentation Status

The stabilization and documentation recovery task TH-0064 is closed. TH-0061.6 is closed after delivery of the single-club recipe component, product, note, and lifecycle workflow. TH-0061.3 and TH-0061.4 are closed because persistent MealPlan and MealSlot composition are implemented; remaining menu rules are tracked by TH-0061.5.

Canonical current documents:

- `PRODUCT_SPEC.md` — approved target product scope;
- `PROJECT_STATUS.md` — verified implementation status;
- `ARCHITECTURE_CURRENT.md` — current architecture and explicitly deferred target boundaries;
- `DOMAIN_CURRENT.md` — current persisted domain and future target model;
- `CURRENT_ROADMAP.md`;
- `TECH_DEBT.md`.

Legacy documents remain historical references and must not override current documents or accepted ADRs.

## Active Work

Current active tasks:

- TH-0061 — guided project preparation journey;
- TH-0061.5 — Meal Composition Rules Engine;
- TH-0065 — Meal Plan Editor UX.

Immediate product sequence:

1. implement meal composition, diversity, and insufficient-catalogue warnings;
2. complete packaging presentation and equipment;
3. finish exports and release acceptance;
4. introduce invitation-only access, roles, multi-variant recipe ownership, and moderation.

## Release Definition

MVP is ready for Product Owner acceptance only when:

- `docker compose up --build` starts the complete local stack;
- backend, frontend, migration, lint, type-check, security, backup/restore, and release gates pass;
- the complete Russian single-club workflow works from project creation through exports on desktop and mobile layouts;
- no P0 debt applicable to the selected single-user release scope remains;
- documentation matches the released code.