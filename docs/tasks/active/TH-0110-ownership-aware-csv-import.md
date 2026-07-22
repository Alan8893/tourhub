# TH-0110 — Ownership-Aware CSV Import

Status: IN PROGRESS

## Goal

Make Recipe CSV import respect the delivered CLUB/PERSONAL ownership model without changing the existing Product import contract or weakening preview/apply safety.

## Product contract

- Product CSV import remains club-wide because Product has no personal ownership model.
- Recipe import requires one explicit target ownership scope for the whole import operation: `CLUB` or `PERSONAL`.
- `PERSONAL` imports are owned by the authenticated user and are visible through the existing personal Recipe lifecycle.
- `CLUB` imports create club-owned Recipes and require existing preparation-level catalogue access.
- Preview and apply must use the same ownership target; apply rejects a stale or mismatched preview contract.
- Imported Recipe components and notes inherit the Recipe identity and do not introduce independent ownership.
- Existing duplicate, reference, alcohol-policy, row/field validation, and all-or-nothing transaction behavior remain mandatory.
- Successful apply keeps semantic actor-aware import audit without exposing CSV payloads or protected data.

## Backend scope

- extend Recipe import preview/apply request and response schemas with an explicit ownership target;
- resolve the authenticated actor as owner for `PERSONAL` imports;
- enforce authorization for `CLUB` imports and mask unavailable targets consistently;
- persist Recipe ownership through the existing ownership fields and lifecycle rules;
- keep Product import API and stored data unchanged;
- add policy, authorization, rollback, stale-preview, and regression tests.

## Frontend scope

- add an ownership selector to the Recipe CSV import workflow;
- explain CLUB versus PERSONAL effects before preview;
- show the selected ownership target in preview and apply confirmation;
- preserve upload, paste, template download, validation, loading, empty, error, and success states;
- keep the workflow responsive and add real-Chrome acceptance.

## Non-goals

- per-row mixed ownership in one CSV;
- ownership changes for existing Recipes;
- Product ownership or personal Product catalogues;
- automatic publication/moderation of imported Recipes;
- bulk import of Projects, Dishes, users, or teams;
- Project copy, audit retention, session cleanup, or notification delivery.

## Data and release

- reuse the existing Recipe ownership columns; no migration is expected;
- Alembic must remain a single head;
- immutable tag `v0.1.0` must remain unchanged;
- existing CSV templates remain backward-compatible except for the explicit UI/API ownership target outside CSV rows.

## Acceptance

- Backend, Frontend, and browser tests cover CLUB and PERSONAL preview/apply;
- unauthorized CLUB import is rejected without writes or audit;
- PERSONAL import records the current user as owner;
- preview/apply ownership mismatch is rejected atomically;
- imported Recipes appear only in the correct existing Recipe catalogue projection;
- all exact-head release gates are green before squash merge.
