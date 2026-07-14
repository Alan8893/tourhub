# TourHub Project Status

Status date: 2026-07-14

## Current Phase

MVP stabilization and documentation recovery.

## Verified Baseline

After stabilization PR #1:

- Alembic has one head: `f10001`;
- backend test suite: 110 tests passed;
- frontend production build: passed;
- MealSlot editing routes are registered in OpenAPI;
- migration revision collision was removed.

## Implemented Product Areas

### Project workflow

Implemented:

- project creation and preparation context;
- participant count and trip duration;
- meal boundary context;
- workspace preparation flow.

Needs completion:

- automatic recalculation after participant-count change;
- finalized Russian adaptive UX;
- complete authorization enforcement.

### Meal plan

Implemented:

- persistent MealPlan domain;
- days and meal schedule;
- MealSlot composition;
- multiple dishes per meal;
- add, remove, and replace dish operations;
- frontend MealSlot editor;
- legacy MealPlanItem compatibility.

Needs completion:

- approved diversity rules;
- manual-versus-generated recipe preference modes;
- recalculation guarantees after edits;
- frontend tests.

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
- PDF, Excel, and package export foundations.

Needs completion:

- recalculation after menu and participant changes;
- complete package/remainder presentation;
- equipment pipeline;
- final Russian templates with logo from settings.

## Quality Status

Passing:

- backend functional tests;
- frontend TypeScript production build;
- Alembic single-head validation.

Open quality debt:

- Ruff violations remain;
- strict mypy errors remain;
- frontend automated tests are absent;
- CI quality gates are not complete;
- dependency audit reports a high-severity Vite issue in the audited snapshot;
- Docker end-to-end verification must be included in release acceptance.

## Documentation Status

Documentation recovery is active.

Known resolved inconsistencies in this cycle:

- product decisions are centralized in `PRODUCT_SPEC.md`;
- current implementation state is centralized here;
- duplicate active copies of closed TH-0061.7, TH-0062, and TH-0063 are removed;
- current roadmap is replaced with a stabilization-first MVP roadmap.

Known remaining documentation work:

- align `PROJECT_CONTEXT.md` with the one-club model;
- align `DOMAIN.md` with approved recipe scopes, invitations, alcohol prohibition, audit log, and equipment rules;
- align `ARCHITECTURE.md` with the implemented MealSlot evolutionary model;
- review duplicate ADR-011 documents and mark one canonical;
- update module/API documentation after each implementation task.

## Active Work

Current task:

- TH-0064 — Project Stabilization and Documentation Recovery.

Next major workstreams:

1. close quality and public API gaps;
2. implement invitation-only access and roles;
3. finish recipe ownership and moderation;
4. finish menu diversity and recalculation;
5. finish packaging, shopping, and equipment;
6. finish exports, audit log, backup/restore, and release acceptance.

## Release Definition

MVP is ready for Product Owner acceptance only when:

- `docker compose up --build` starts the complete local stack;
- backend, frontend, migration, lint, type-check, and security gates pass;
- the complete Russian user scenario works from invitation through exports;
- backup and restore are documented and verified;
- documentation matches the released code.
