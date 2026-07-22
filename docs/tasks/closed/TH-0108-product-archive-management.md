# TH-0108 — Product Archive Management

Status: DONE

## Goal

Allow preparation users to archive and restore Product catalogue records without deleting historical references, while preserving the central alcohol prohibition and keeping archive policy Backend-owned.

## Delivered

- default `GET /api/v1/products` remains active-only and keeps its stable response contract;
- protected `GET /api/v1/products/archive` returns archived Products with archive and alcohol-policy lock state;
- `POST /api/v1/products/{id}/archive` performs soft archive under a row lock;
- `POST /api/v1/products/{id}/restore` restores only manually archived Products still allowed by the central alcohol policy;
- `archived_by_alcohol_policy=true` records remain non-restorable and return HTTP 409;
- archive and restore are idempotent and do not create duplicate AuditEvents;
- Product rows and historical Recipe, purchase, checklist, and document references are never deleted;
- `product_archived` and `product_restored` commit or roll back with the Product state change;
- the existing Recipe component catalogue exposes a responsive Product archive-management dialog;
- active and archived views include loading, empty, success, error, policy-lock, archive, and restore states;
- Backend, Frontend helper, Product Acceptance, full browser acceptance, and an isolated real-Chrome scenario cover the capability;
- no migration was required; Alembic remains at `h10023` and immutable tag `v0.1.0` remains unchanged.

## Backend policy

- archive and restore require `require_preparation_access`;
- archive is soft and changes only `is_archived`;
- active Product selection excludes archived rows;
- archived rows are exposed only through the explicit management endpoint;
- row state and semantic audit share one transaction;
- restore re-runs `AlcoholPolicy.require_product_allowed` against stored name and category;
- alcohol-policy archive markers cannot be cleared by this capability;
- existing Recipe/Product response contracts remain stable; archive state uses separate response schemas.

## Non-goals retained

- Dish archive management;
- Recipe lifecycle or archive changes;
- physical Product deletion or cascading cleanup;
- bulk archive or restore;
- editing an archived Product;
- overriding the central alcohol prohibition;
- ownership-aware CSV import UX;
- audit retention UI, session cleanup, global sign-out, Administrator session administration, or `Копировать проект`;
- multi-tenant support, microservices, or moving release tag `v0.1.0`.

## Verification

- Backend tests cover reference preservation, active/archive projections, idempotency, policy lock, audit contents, and rollback;
- Frontend tests cover restore eligibility and policy explanation;
- real Chrome archives and restores a Product, verifies requests, confirms policy-locked restore is disabled, and checks mobile overflow;
- exact-head Quality, Product Acceptance, Docker Release Runtime, Document Quality, Guided Release Acceptance, Operator Docs, and Final Release Readiness passed on the implementation head before final task-state synchronization.
