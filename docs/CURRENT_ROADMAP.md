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

- Alembic: one head (`f10001`).
- Backend: 110 tests passed.
- Frontend: production build passed.
- MealSlot editing API is present in OpenAPI.
- Project, MealPlan, MealSlot, RecipeComponent, shopping, checklist, and export foundations exist.

## Milestone 1 — Stabilization and Documentation Recovery

Status: ACTIVE

Goals:

- synchronize product decisions and implemented behavior;
- remove duplicate task states;
- eliminate public API placeholders;
- restore enforceable quality gates;
- add CI;
- verify Docker startup.

Primary task:

- TH-0064 — Project Stabilization and Documentation Recovery.

Exit criteria:

- documentation is internally consistent;
- backend tests pass;
- frontend build passes;
- Alembic has one head;
- public API has no accidental placeholders;
- agreed Ruff/mypy baseline is enforced;
- CI and Docker verification exist.

## Milestone 2 — Closed Access and Administration

Status: PLANNED

Goals:

- invitation-only registration;
- Administrator, Instructor, and Verified Instructor roles;
- role-based permissions;
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
- automatic recalculation after participant-count and menu changes without regenerating selected dishes.

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

Status: PLANNED

Goals:

- Russian PDF with club logo from settings;
- Russian Excel workbook with trip, menu, loadout, shopping, and equipment sheets;
- safe audit trail;
- PostgreSQL backup and restore scripts;
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

## Future Modules

Not part of MVP:

- participant profiles and personal data;
- price aggregator integration;
- warehouse stock accounting;
- routes and GPX;
- logistics and load distribution;
- external or paid services;
- multi-tenant support.
