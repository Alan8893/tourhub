# TH-0109 — Dish Archive Management

Status: DONE

## Goal

Allow preparation users to archive and restore Dish catalogue records without deleting Recipes, MealSlot assignments, historical calculations, exports, or audit references, while keeping lifecycle policy Backend-owned and the existing active Dish catalogue contract stable.

## Delivered

- the default `GET /api/v1/dishes` projection remains active-only and keeps the established `DishResponse` contract;
- protected `GET /api/v1/dishes/archive` returns archived Dishes with recipe display data and central-policy lock state;
- protected `POST /api/v1/dishes/{id}/archive` performs a soft archive under a row lock;
- protected `POST /api/v1/dishes/{id}/restore` restores only manually archived Dishes still accepted by the central alcohol policy;
- `archived_by_alcohol_policy=true` Dishes remain non-restorable and return HTTP 409;
- archive and restore are idempotent and do not create duplicate AuditEvents;
- Dish rows, Recipe variants, meal-role assignments, and historical MealSlot/project references are never deleted;
- `dish_archived` and `dish_restored` commit or roll back with the Dish state change;
- the existing Dishes workspace exposes a responsive active/archive management dialog;
- the UI covers loading, empty, success, error, policy-lock, archive, restore, and mobile states;
- Backend policy tests, Frontend helper tests, and an isolated real-Chrome scenario cover the capability;
- no migration was required because the Dish archive columns already existed; Alembic remains `h10023` and immutable tag `v0.1.0` remains unchanged.

## Backend policy

- archive management requires `require_preparation_access`;
- archive changes only `is_archived` and never physically deletes a Dish;
- active Dish selection excludes archived rows while historical relationships remain readable;
- archived rows are exposed only through the explicit management projection or existing historical resources;
- row state and semantic audit share one transaction;
- restore re-runs `AlcoholPolicy.require_dish_name_allowed` against the stored Dish name;
- alcohol-policy archive markers cannot be cleared by this capability;
- existing Dish and Recipe response contracts remain stable because archive state uses dedicated response schemas.

## Non-goals retained

- Product or Recipe lifecycle changes;
- physical Dish deletion or cascading cleanup;
- bulk archive or restore;
- editing an archived Dish;
- ownership-aware CSV import UX;
- audit retention UI, session cleanup, global sign-out, Administrator session administration, or `Копировать проект`;
- multi-tenant support, microservices, or moving release tag `v0.1.0`.

## Verification

- Backend tests cover active/archive projections, Recipe-reference preservation, idempotency, policy lock, audit contents, and transactional rollback;
- Frontend tests cover restore eligibility and safe policy explanation;
- real Chrome archives and restores a Dish, verifies requests, confirms policy-locked restore is disabled, and checks mobile horizontal overflow;
- Quality, Product Acceptance, Docker Release Runtime, Document Quality, Guided Release Acceptance, Operator Docs, and Final Release Readiness are required on the exact final head before squash merge.
