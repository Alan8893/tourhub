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
- ADR-012 accepted for single-club, invitation-only deployment boundaries.

Remaining:

- remove public API placeholders;
- improve MealSlot error and recalculation contracts;
- resolve dependency vulnerability;
- establish Ruff/mypy gates;
- add frontend tests and CI;
- verify Docker startup, migrations, backup, and restore;
- complete final legacy-document reconciliation before closing TH-0064.
