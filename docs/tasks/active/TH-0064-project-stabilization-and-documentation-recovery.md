# TH-0064 — Project Stabilization and Documentation Recovery

Status: ACTIVE

## Goal

Create a reliable technical and documentary baseline before continuing MVP feature development.

## Context

The repository contains a functional backend and significant frontend/domain implementation, but code, migrations, task documents, ADRs, and roadmap evolved at different speeds.

The audit identified:

- duplicate active and closed task documents;
- stale roadmap verification results;
- contradictory MealSlot and organization architecture documentation;
- a duplicate Alembic revision, fixed in PR #1;
- frontend build failure, fixed in PR #1;
- Ruff and strict mypy backlogs;
- absent frontend tests and incomplete CI;
- public API placeholders and incomplete Docker release verification.

## Scope

### Documentation recovery

- add approved product specification;
- add current project status;
- add prioritized technical debt register;
- replace stale current roadmap;
- remove duplicate active copies of closed tasks;
- synchronize project context, domain, architecture, ADRs, and development rules.

### Technical stabilization

- remove or implement public API placeholders;
- improve MealSlot error contracts and recalculation verification;
- fix dependency vulnerabilities;
- establish Ruff and mypy clean baselines;
- add frontend tests for critical workflows;
- add GitHub Actions quality gates;
- verify Docker startup and migrations.

## Constraints

- do not change the approved technology stack;
- do not introduce microservices;
- do not introduce multi-tenant behavior;
- do not use paid services;
- preserve existing working user flows;
- use evolutionary migrations when existing data may be affected.

## Definition of Done

- product decisions are documented in `docs/PRODUCT_SPEC.md`;
- current implementation is documented in `docs/PROJECT_STATUS.md`;
- roadmap and task statuses are consistent;
- no duplicate active/closed task remains;
- relevant ADRs match implemented architecture;
- Alembic reports one head;
- backend tests pass;
- frontend tests, type-check, and build pass;
- Ruff and agreed mypy gates pass;
- public API contains no accidental placeholders;
- CI validates the quality gates;
- `docker compose up --build` is documented and verified;
- remaining work is represented by active tasks or `docs/TECH_DEBT.md`.

## Progress

Completed:

- repository audit performed;
- Alembic revision collision fixed;
- frontend production build restored;
- MealSlot OpenAPI contract test added;
- approved product specification added;
- project status and technical debt register added;
- stale roadmap replaced;
- duplicate active copies of TH-0061.7, TH-0062, and TH-0063 removed;
- canonical current architecture and domain baselines added;
- development workflow and Definition of Done formalized;
- ADR-012 accepted for single-club, invitation-only deployment boundaries;
- accidental public API placeholder removed;
- legacy MealPlan placeholder route removed;
- missing MealSlot dish operations return an explicit `404` contract;
- GitHub Actions quality workflow added for backend tests, Alembic single-head validation, selected Ruff and mypy baselines, frontend dependency audit, and production build;
- backend Docker startup now waits for PostgreSQL readiness and applies `alembic upgrade head` before Uvicorn;
- full local stack startup, migrations, project creation, menu generation, preparation, and document exports verified through `docker compose up --build` after PR #24;
- frontend API requests verified to use `/api/v1/...` after removal of the stale generated Vite config;
- dependency-free frontend test baseline added with Node.js built-in test runner for MealPlan loading, error, empty, and ready presentation states;
- GitHub Actions frontend job extended to run the frontend test baseline before the production build;
- MealSlot add, replace, and remove commands covered by deterministic frontend tests;
- MealSlot pending and mutation-error states covered by deterministic frontend tests;
- MealSlot editing controls localized to Russian and mutation failures surfaced to the user;
- successful MealSlot and participant-count purchasing recalculation covered by API tests;
- failed MealSlot and participant-count recalculation now explicitly rolls back the database transaction;
- rollback and commit behavior covered by backend regression tests;
- MealSlot application service typed and added to the enforced Ruff and mypy workflow baseline;
- PostgreSQL custom-format backup and restore procedures documented for Bash and PowerShell;
- CI backup/restore smoke test added against the PostgreSQL 18 Compose service.

Remaining:

- extend recalculation verification to the future equipment pipeline when equipment persistence is implemented;
- resolve the reported frontend dependency vulnerability;
- continue expanding Ruff and mypy from the stabilized workflow baseline to the agreed repository baseline;
- expand frontend tests to responsive workflows and higher-level interaction coverage;
- extend CI with the remaining agreed release gates;
- complete final legacy-document reconciliation before closing TH-0064.
