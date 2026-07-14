# TourHub Project Status

Status date: 2026-07-14

## Current Phase

Single-club product completion. Multi-user access and administration are intentionally deferred while the recipe, dish, menu, shopping, and export workflow is completed.

## Verified Baseline

- Alembic has one head: `g10001`.
- Backend functional tests pass in GitHub Actions.
- Selected Ruff and strict mypy baselines are enforced in GitHub Actions.
- Frontend state tests, moderate-severity dependency audit, TypeScript check, and production build pass in GitHub Actions.
- PostgreSQL 18 backup and restore are smoke-tested in GitHub Actions.
- MealSlot editing routes are registered in OpenAPI.
- Full local stack startup, automatic migrations, project creation, menu generation, preparation, and exports were verified during the stabilization cycle.

## Implemented Product Areas

### Project workflow

Implemented:

- project creation and preparation context;
- participant count and trip duration;
- meal boundary context;
- workspace preparation flow;
- participant-count purchasing recalculation with transactional rollback.

Needs completion:

- finalized Russian adaptive UX;
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

- approved diversity rules;
- explicit recipe selection for dishes;
- responsive and higher-level interaction tests;
- TH-0065 Meal Plan Editor UX acceptance.

### Recipes

Implemented:

- Dish and Recipe separation foundation;
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
- shopping integration with legacy fallback;
- regression coverage for read, write, validation, archive, restore, and delete flows.

Needs completion:

- dish catalogue and explicit dish-to-recipe management;
- preparation technology, equipment, dietary, season, and category metadata;
- alcohol prohibition validation;
- ownership, publication, and moderation after multi-user mode is introduced.

### Shopping and documents

Implemented:

- ingredient aggregation;
- shopping list;
- purchase checklist;
- package rounding foundation;
- recalculation after participant and MealSlot changes;
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

The stabilization and documentation recovery task TH-0064 is closed. TH-0061.6 is closed after delivery of the single-club recipe component, product, note, and lifecycle workflow.

Canonical current documents:

- `PRODUCT_SPEC.md`;
- `PROJECT_STATUS.md`;
- `ARCHITECTURE_CURRENT.md`;
- `DOMAIN_CURRENT.md`;
- `CURRENT_ROADMAP.md`;
- `TECH_DEBT.md`.

Legacy documents remain historical references and must not override current documents or accepted ADRs.

## Active Work

Current active task:

- TH-0065 — Meal Plan Editor UX.

Immediate product sequence:

1. finish dish catalogue and explicit recipe selection;
2. finish menu diversity and preference modes;
3. finish packaging, shopping, and equipment;
4. finish exports and release acceptance;
5. introduce invitation-only access, roles, ownership, and moderation.

## Release Definition

MVP is ready for Product Owner acceptance only when:

- `docker compose up --build` starts the complete local stack;
- backend, frontend, migration, lint, type-check, security, backup/restore, and release gates pass;
- the complete Russian single-club workflow works from project creation through exports on desktop and mobile layouts;
- no P0 debt applicable to the selected single-user release scope remains;
- documentation matches the released code.