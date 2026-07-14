# TourHub Project Status

Status date: 2026-07-14

## Current Phase

Closed-access and administration planning after completion of the stabilization baseline.

## Verified Baseline

- Alembic has one head: `f10001`.
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

- invitation-only authorization enforcement;
- finalized Russian adaptive UX;
- equipment-dependent recalculation after the equipment domain is implemented.

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
- manual-versus-generated recipe preference modes;
- responsive and higher-level interaction tests;
- TH-0065 Meal Plan Editor UX acceptance.

### Recipes

Implemented:

- Dish and Recipe separation;
- RecipeComponent layer;
- component types;
- recipe notes;
- practical quantity calculation modes;
- shopping integration with legacy fallback.

Needs completion:

- CLUB/PERSONAL/ARCHIVED scopes;
- invitation-based user ownership;
- publication and moderation workflow;
- full metadata, equipment, dietary, and season fields;
- alcohol prohibition validation.

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

The stabilization and documentation recovery task TH-0064 is closed.

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

Next major workstreams:

1. implement invitation-only access and roles;
2. finish recipe ownership, moderation, and alcohol prohibition;
3. finish menu diversity and preference modes;
4. finish packaging, shopping, and equipment;
5. finish exports, audit log, and release acceptance.

## Release Definition

MVP is ready for Product Owner acceptance only when:

- `docker compose up --build` starts the complete local stack;
- backend, frontend, migration, lint, type-check, security, backup/restore, and release gates pass;
- the complete Russian user scenario works from invitation through exports on desktop and mobile layouts;
- no P0 debt remains;
- documentation matches the released code.
