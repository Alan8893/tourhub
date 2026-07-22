# TH-0108 — Product Archive Management

Status: IN PROGRESS

## Goal

Allow preparation users to archive and restore Product catalogue records without deleting historical references, while preserving the central alcohol prohibition and keeping archive policy Backend-owned.

## Scope

- expose Product archive state in Backend response schemas;
- keep the default Product catalogue read active-only;
- add an explicit archived-product read for archive management;
- allow an authorized preparation user to archive one active Product;
- allow restoration of a manually archived Product only when the central alcohol policy still permits it;
- permanently block restoration of records marked `archived_by_alcohol_policy`;
- record safe semantic `product_archived` and `product_restored` AuditEvents in the same transaction as state changes;
- add an archive-management section to the Product catalogue UI with loading, empty, success, and failure states;
- add Backend, Frontend, and real-Chrome acceptance;
- keep one Alembic head and preserve immutable tag `v0.1.0`.

## Backend policy

- archive and restore routes require `require_preparation_access`;
- archive is soft: it changes `is_archived` and never deletes Product, Recipe component, purchase, checklist, or generated-document history;
- active list remains the default source for Recipe and preparation selection;
- archived records are returned only through an explicit archive-management query;
- archive and restore lock the Product row and commit state plus audit as one transaction;
- archiving an already archived Product and restoring an active Product are idempotent reads with no duplicate audit event;
- restore re-runs `AlcoholPolicy.require_product_allowed` against stored name/category;
- `archived_by_alcohol_policy=true` cannot be cleared or restored through this capability;
- no raw request data, credentials, headers, or unrelated catalogue contents enter audit payloads.

## Non-goals

- Dish archive management;
- Recipe lifecycle or archive behavior;
- physical Product deletion or cascading cleanup;
- bulk archive/restore;
- changing Product names, categories, units, or package sizes while archived;
- overriding the central alcohol prohibition;
- ownership-aware CSV import UX;
- audit retention UI, session cleanup, global sign-out, Administrator session administration, or `Копировать проект`;
- multi-tenant support, microservices, or moving release tag `v0.1.0`.

## Acceptance

### Backend

- default `GET /api/v1/products` returns active Products only;
- explicit archived read returns archived Products with `is_archived` and policy-lock state;
- archive removes a Product from the active list without deleting references;
- restore returns a manually archived allowed Product to the active list;
- alcohol-policy archived Products remain non-restorable and return a deterministic conflict/validation response;
- archive/restore are idempotent and do not duplicate audit events;
- forced audit failure rolls back archive state;
- response and audit data exclude secrets and unrelated records.

### Frontend

- Product catalogue exposes a clear archive action for active records;
- archived records are available in a separate archive-management view;
- a manually archived record has a restore action;
- an alcohol-policy archived record visibly explains why restore is unavailable;
- progress, success, empty, and error states are explicit;
- active editor and archived view remain usable without horizontal overflow at accepted mobile width.

### Real Chrome

- an authenticated preparation user opens the Product catalogue;
- archives one Product and sees it disappear from the active list;
- opens archived Products and restores the manually archived Product;
- observes a policy-locked archived Product without a restore action;
- verifies expected Backend archive/restore requests;
- mobile layout has no horizontal overflow.

## Migration

No migration is expected because `products.is_archived` and `products.archived_by_alcohol_policy` already exist. Alembic head remains `h10023` unless implementation proves a persistence change is required.
