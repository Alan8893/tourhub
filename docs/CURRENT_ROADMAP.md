# TourHub Current Roadmap

Status date: 2026-07-14

## Product Goal

Deliver a stable local MVP for one tourist club.

The complete user journey is:

```text
Administrator invites user
        ↓
Instructor creates project
        ↓
Instructor enters dates, participant count, first and last meal
        ↓
System generates a diverse editable menu
        ↓
Instructor selects club or personal recipe variants
        ↓
System calculates ingredients and packages
        ↓
System produces shopping and equipment lists
        ↓
Instructor reviews and adjusts results
        ↓
System exports Russian PDF and Excel documents
```

## Verified Baseline

- Alembic has one head (`f10001`).
- Backend tests pass in GitHub Actions.
- Selected Ruff and strict mypy baselines are enforced.
- Frontend state tests, moderate-severity dependency audit, TypeScript check, and production build pass.
- PostgreSQL 18 backup and restore are smoke-tested in GitHub Actions.
- MealSlot editing and purchasing recalculation are implemented with transactional rollback coverage.
- Docker Compose startup, automatic migrations, project creation, menu generation, preparation, and exports were verified during the stabilization cycle.

## Milestone 1 — Stabilization and Documentation Recovery

Status: COMPLETE

Completed through TH-0064:

- synchronized product, domain, architecture, status, roadmap, technical debt, and development rules;
- removed duplicate task states, migration collision, and accidental public placeholders;
- established backend, frontend, migration, dependency, and backup/restore CI gates;
- verified local Docker startup and primary implemented workflow;
- documented and tested PostgreSQL backup and restore.

## Milestone 2 — Closed Access and Administration

Status: NEXT

Goals:

- invitation-only registration;
- Administrator, Instructor, and Verified Instructor roles;
- role-based permissions enforced by the backend;
- user and invitation administration;
- audit log foundation;
- local-only security configuration.

## Milestone 3 — Recipe Library and Moderation

Status: PLANNED

Goals:

- CLUB, PERSONAL, and ARCHIVED recipe scopes;
- club standards and instructor variants;
- verified-instructor publication and moderation;
- preparation technology, notes, equipment, tags, categories, season, and dietary metadata;
- hard alcohol prohibition;
- safe archival instead of destructive deletion.

## Milestone 4 — Menu Intelligence and Recalculation

Status: PLANNED

Goals:

- required meal schedule with first/last boundaries;
- one-day trip handling;
- automatic generation unless manually selected;
- three-day main-dish diversity;
- same-day uniqueness;
- club/personal preference modes;
- warnings when the catalogue is insufficient;
- automatic recalculation after participant-count and menu changes without regenerating selected dishes;
- extend recalculation to dependent equipment after the equipment domain is implemented.

## Milestone 5 — Shopping, Packaging, and Equipment

Status: PLANNED

Goals:

- aggregate identical products;
- round package counts upward;
- expose required, purchased, and remainder quantities;
- purchased status, category, comments, and optional responsible person;
- aggregate recipe equipment by maximum simultaneous requirement;
- manual equipment overrides.

Prices, stores, price aggregators, and warehouse balances remain future work.

## Milestone 6 — Documents and Local Operations

Status: IN PROGRESS

Completed:

- PostgreSQL backup and restore scripts;
- Bash and PowerShell operational instructions;
- CI backup/restore verification.

Remaining:

- Russian PDF with club logo from settings;
- Russian Excel workbook with trip, menu, loadout, shopping, and equipment sheets;
- safe audit trail;
- complete local installation and update documentation.

## Milestone 7 — MVP Acceptance

Status: PLANNED

Acceptance requires:

- `docker compose up --build` starts the complete system;
- all automated quality gates pass;
- the complete user journey works in Russian on desktop and mobile layouts;
- backup and restore are verified;
- no P0 debt remains;
- documentation matches the release;
- Product Owner completes local acceptance.

## Active Cross-cutting Work

- TH-0065 — Meal Plan Editor UX;
- incremental Ruff and strict mypy expansion;
- higher-level and responsive frontend tests;
- remaining Docker image/build and release gates.

## Future Modules

Not part of MVP:

- participant profiles and personal data;
- price aggregator integration;
- warehouse stock accounting;
- routes and GPX;
- logistics and load distribution;
- external or paid services;
- multi-tenant support.
