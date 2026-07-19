# TH-0092 — Product Acceptance and Feature Freeze

Status: CLOSED

Last updated: 2026-07-19

## Goal

Formally accept the approved first-release product scope, prove the critical workflows through one dedicated CI gate, explicitly defer optional scope, and freeze feature development before final migration/release readiness.

## Scope

### Acceptance evidence

- validate one machine-readable release-scope manifest;
- run selected real Backend API scenarios for access, roles, catalogue/import, Recipe publication, alcohol policy, preparation readiness, audit, and complete documents;
- run selected real Chrome scenarios for authentication/route return, user administration, Recipe moderation, audit, consolidated documents, and guided create-to-ZIP flow;
- retain the existing full Quality, Document, Guided, Operator, PostgreSQL, and Docker gates.

### Product decision

- update the completeness matrix against the accepted release baseline;
- mark every approved release-blocking capability accepted or explicitly deferred;
- classify optional gaps as non-blocking deferred scope;
- record Alembic head `h10021` and the final functional PR sequence;
- set feature-freeze rules: only acceptance defects, release-readiness work, security fixes, and documentation corrections may change first-release scope.

### Documentation

- add `PRODUCT_ACCEPTANCE.md`;
- add a versioned JSON acceptance manifest;
- add a validator and dedicated Product Acceptance workflow;
- synchronize status, roadmap, context, technical debt, task index, and README after acceptance passes.

## Out of scope

- new Product/Recipe/Project features;
- reopening explicitly deferred optional scope;
- final previous → head → previous → head PostgreSQL cycle;
- release tag, deployment checklist, or final release workflow;
- performance/load testing beyond current local single-club operating model.

## Acceptance result

- the manifest gate passed with eight accepted capability groups and Alembic head `h10021`;
- Ruff passed for `scripts/ci/validate_product_acceptance.py` after canonical import-block formatting;
- the selected real Backend API/migration suite passed;
- all six critical Chrome scenarios passed;
- the acceptance manifest is `feature_frozen`;
- no active release-blocking capability remains;
- deferred scope is explicit and non-blocking;
- current documents name Final Migration and Release Readiness as the only next phase.

Acceptance evidence commit: `ce05a181242d2888f25a8bccc1794ebbc422046a`.

## Definition of done

- [x] the dedicated Product Acceptance workflow passes on the exact acceptance evidence head;
- [x] all existing repository workflows remain required on the final PR exact head;
- [x] the manifest state is `feature_frozen`;
- [x] no active release-blocking capability remains;
- [x] deferred scope is explicit and non-blocking;
- [x] current docs name Final Migration and Release Readiness as the only next phase.

## Next phase

Final Migration and Release Readiness owns the PostgreSQL previous → `h10021` → previous → `h10021` cycle, deployment checklist, final release workflow, and release tag after green exact-head gates.
