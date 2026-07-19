# TH-0093 — Final Migration and Release Readiness

Status: IN PROGRESS

Last updated: 2026-07-19

## Goal

Prove that the accepted feature-frozen first release can complete its final PostgreSQL migration cycle and production-like deployment checks, then add the final release gate and create the release tag only from one green exact head.

## Accepted baseline

- Product scope is feature frozen by TH-0092 / PR #102.
- Alembic previous revision: `h10020`.
- Alembic accepted head: `h10021`.
- Deployment model: local single-club modular monolith.
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, and Docker Release Runtime passed on the final TH-0092 head.

## Scope

### Final migration cycle

- add one deterministic PostgreSQL 18 verification for `h10020 → h10021 → h10020 → h10021`;
- seed representative allowed, prohibited, manually archived, historically referenced, and policy-archived catalogue data before the first upgrade;
- verify archive markers, active-catalogue filtering, historical relationships, and downgrade restoration semantics after every transition;
- verify the final database revision is exactly `h10021` and Alembic retains one head;
- preserve evidence when a migration step fails.

### Deployment readiness

- add one versioned production-like deployment checklist covering prerequisites, configuration, secrets, backup, upgrade, health, LAN access, smoke acceptance, rollback boundary, and operator sign-off;
- verify the checklist against `docker-compose.release.yml`, installation/update/recovery documentation, health endpoints, backup/restore scripts, and existing runtime workflows;
- ensure no release service depends on a paid or external runtime service.

### Final release gate

- add a final release-readiness workflow that composes, rather than duplicates, the accepted migration, Product Acceptance, Quality, document, guided, operator, backup/restore, and Docker evidence;
- bind the final decision to one exact commit SHA and accepted manifest state `feature_frozen`;
- prevent release tagging when any required exact-head workflow is missing, pending, skipped, cancelled, or failed;
- document the approved tag format and release notes source;
- create the release tag only after all exact-head gates pass.

### Documentation and closeout

- synchronize `PROJECT_STATUS.md`, `PROJECT_CONTEXT.md`, `CURRENT_ROADMAP.md`, `TECH_DEBT.md`, `README.md`, operator documentation, and the task index;
- close TH-0093 only after the tag and release evidence are recorded;
- leave all deferred capabilities explicitly non-blocking and unchanged.

## Out of scope

- new Product, Recipe, Project, Access, mail, audit, document, catalogue, participant, route, warehouse, procurement, or logistics capabilities;
- reopening deferred scope;
- architecture, stack, multi-tenancy, or microservice changes;
- a new Alembic revision unless a reproducible acceptance defect or security issue proves it necessary and the Product Owner approves the scope impact;
- performance/load expansion beyond the accepted local single-club model;
- paid or externally hosted release services.

## Definition of done

- [ ] PostgreSQL 18 passes `h10020 → h10021 → h10020 → h10021` with representative data and final revision `h10021`;
- [ ] Alembic has exactly one head;
- [ ] the deployment checklist is versioned, executable, and verified against the release stack;
- [ ] Product Acceptance remains `feature_frozen` and green;
- [ ] all required repository workflows pass on one exact head;
- [ ] final release-readiness evidence is machine-readable and human-readable;
- [ ] the release tag is created from the verified exact head;
- [ ] current documentation records the released state and rollback boundary;
- [ ] TH-0093 is moved to `docs/tasks/closed/` with no release-blocking debt remaining.

## First implementation step

Inventory the existing migration, PostgreSQL backup/restore, release runtime, and operator gates; design the smallest deterministic exact-head workflow that verifies the migration cycle without duplicating existing acceptance coverage.
