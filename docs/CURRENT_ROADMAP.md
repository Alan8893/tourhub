# TourHub Current Roadmap

Status date: 2026-07-15

## Product Goal

Deliver a stable local MVP for one tourist club.

The immediate single-user journey is:

```text
Instructor creates project
        ↓
Instructor enters dates, participant count, first and last meal
        ↓
System generates a diverse editable menu
        ↓
Instructor selects and edits dishes and recipes
        ↓
System calculates ingredients and packages
        ↓
System produces shopping and equipment lists
        ↓
Instructor reviews and adjusts results
        ↓
System exports Russian PDF and Excel documents
```

Invitation-only access, roles, ownership, and moderation remain required for the later multi-user phase, but do not block completion of the current single-club workflow.

## Verified Baseline

- Alembic has one head (`g10001`).
- Backend tests pass in GitHub Actions.
- Selected Ruff and strict mypy baselines are enforced.
- Frontend state tests, moderate-severity dependency audit, TypeScript check, and production build pass.
- PostgreSQL 18 backup and restore are smoke-tested in GitHub Actions.
- Project catalogue, MealSlot editing, dish recipe replacement, and purchasing recalculation are implemented with transactional rollback coverage.
- The single-club recipe library supports products, components, notes, archive, restore, guarded deletion, and transactional CSV import through API and frontend.
- Docker Compose startup, automatic migrations, project creation, menu generation, preparation, and exports were verified during the stabilization cycle.

## Milestone 1 — Stabilization and Documentation Recovery

Status: COMPLETE

Completed through TH-0064:

- synchronized product, domain, architecture, status, roadmap, technical debt, and development rules;
- removed duplicate task states, migration collision, and accidental public placeholders;
- established backend, frontend, migration, dependency, and backup/restore CI gates;
- verified local Docker startup and primary implemented workflow;
- documented and tested PostgreSQL backup and restore.

## Milestone 2 — Single-club Recipe Library

Status: COMPLETE

Completed:

- recipe list and detail API;
- recipe creation and renaming;
- product catalogue reading and creation;
- RecipeComponent CRUD with practical quantity modes;
- recipe note CRUD and priority ordering;
- active and archived library views;
- safe archive and restore;
- guarded physical deletion when a dish references a recipe;
- complete frontend editor and lifecycle management;
- transactional CSV preview/import for products, recipes, components, and notes;
- regression coverage and CI enforcement.

Deferred to multi-user mode:

- CLUB and PERSONAL ownership scopes;
- publication review and verified-instructor moderation.

## Milestone 3 — Dish Catalogue and Recipe Selection

Status: COMPLETE

Completed:

- dish catalogue API and frontend;
- dish creation and renaming;
- explicit active-recipe assignment and replacement;
- historical visibility when an assigned recipe is archived later;
- prevention of new archived-recipe assignment;
- guarded recipe deletion when referenced by a dish;
- project catalogue at `/projects` with navigation to individual workspaces;
- transactional recalculation of affected purchase lists and checklists after dish recipe replacement;
- preservation of checklist progress for products that remain in the recalculated result.

Current persistence deliberately stores one selected `recipe_id` per Dish. Multiple recipe variants, preferences, ownership, and moderation remain target-domain work for later milestones.

## Milestone 4 — Menu Intelligence and Recalculation

Status: NEXT

Goals:

- required meal schedule with first/last boundaries;
- one-day trip handling;
- automatic generation unless manually selected;
- three-day main-dish diversity;
- same-day uniqueness;
- recipe preference modes after multi-variant recipes are introduced;
- warnings when the catalogue is insufficient;
- impact preview before changing a dish recipe used by existing projects;
- extend recalculation to dependent equipment after the equipment domain is implemented.

Already implemented recalculation triggers:

- participant-count change;
- MealSlot add, remove, and replace;
- assigned recipe replacement on a Dish.

## Milestone 5 — Shopping, Packaging, and Equipment

Status: PLANNED

Goals:

- complete package and remainder presentation;
- expose required, purchased, and remainder quantities consistently;
- purchased status, category, comments, and optional responsible person;
- aggregate recipe equipment by maximum simultaneous requirement;
- manual equipment overrides.

Ingredient aggregation and upward package rounding foundations already exist. Prices, stores, price aggregators, and warehouse balances remain future work.

## Milestone 6 — Documents and Local Operations

Status: IN PROGRESS

Completed:

- PostgreSQL backup and restore scripts;
- Bash and PowerShell operational instructions;
- CI backup/restore verification.

Remaining:

- Russian PDF with club logo from settings;
- Russian Excel workbook with trip, menu, loadout, shopping, and equipment sheets;
- complete local installation and update documentation.

## Milestone 7 — Multi-user Access and Administration

Status: DEFERRED

Goals:

- invitation-only registration;
- Administrator, Instructor, and Verified Instructor roles;
- role-based permissions enforced by the backend;
- user and invitation administration;
- recipe ownership, publication, and moderation;
- audit log foundation;
- local-only security configuration.

## Milestone 8 — MVP Acceptance

Status: PLANNED

Acceptance requires:

- `docker compose up --build` starts the complete system;
- all automated quality gates pass;
- the complete selected release journey works in Russian on desktop and mobile layouts;
- backup and restore are verified;
- no P0 debt applicable to the selected release scope remains;
- documentation matches the release;
- Product Owner completes local acceptance.

## Active Cross-cutting Work

- TH-0061 — complete the guided project preparation journey;
- TH-0061.5 — meal composition and menu diversity rules;
- TH-0065 — Meal Plan Editor UX;
- incremental Ruff and strict mypy expansion;
- higher-level and responsive frontend tests;
- remaining Docker image/build and release gates.

## Future Modules

Not part of the current single-club MVP:

- participant profiles and personal data;
- price aggregator integration;
- warehouse stock accounting;
- routes and GPX;
- logistics and load distribution;
- external or paid services;
- multi-tenant support.