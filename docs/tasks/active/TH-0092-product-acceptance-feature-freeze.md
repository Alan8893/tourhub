# TH-0092 — Product Acceptance and Feature Freeze

Status: IN PROGRESS

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

- update the completeness matrix against current `main`;
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

## Definition of done

- the dedicated Product Acceptance workflow passes on the exact head;
- all existing repository workflows remain green;
- the manifest state is `feature_frozen`;
- no active release-blocking capability remains;
- deferred scope is explicit and non-blocking;
- current docs name Final Release Readiness as the only next phase.
