# TourHub Current Architecture

Status: Active

Last updated: 2026-07-22

TourHub is a single-club modular monolith with PostgreSQL in production.

## Current decisions

- System Settings use independent typed owners under one responsive surface: ADR-014.
- Accounts, roles, invitations, and user administration follow ADR-015 through ADR-017.
- Preparation access follows ADR-018.
- Working mail delivery follows ADR-019.
- Recipe ownership/lifecycle/variants follow ADR-020 through ADR-022.
- Actor-aware audit follows ADR-023.
- Consolidated exports follow ADR-024.
- Central alcohol prohibition follows ADR-025.
- Project ownership and team-scoped access follow ADR-026.
- Global User roles remain singular; Project owner/additional instructor remain Project-scoped.
- Module visibility is presentation-only and never grants access.
- Audit CSV export is a Backend-owned read projection over sanitized AuditEvent persistence.
- Own-session listing and revocation extend the existing server-session boundary without tracking or cross-user administration.
- Product and Dish archive management are separate Backend-owned soft-lifecycle boundaries.

## Access runtime

- one User may own multiple independent server sessions;
- PostgreSQL stores only session-token hashes and session metadata;
- Backend resolves the persisted User on every authorized request;
- deactivation revokes sessions and removes runtime Project access without deleting history;
- `/account` projects only the current User's active sessions;
- recovery, global sign-out, Administrator session administration, cleanup, and retention remain future work.

## Product archive boundary — TH-0108

`ProductArchiveService` is authoritative for Product soft archive and restoration.

### Projection

- the established `GET /api/v1/products` contract remains active-only and unchanged;
- `GET /api/v1/products/archive` requires preparation access and uses a separate archive response schema;
- the archive projection contains Product identity/display fields, `is_archived`, and `archived_by_alcohol_policy`;
- Recipe component selectors continue to consume only the active list;
- Frontend displays Backend state and does not infer restore eligibility.

### Mutation

- archive and restore target the Product by ID under `SELECT ... FOR UPDATE`;
- archive changes only `is_archived` and never deletes the Product or dependent history;
- repeated archive of an archived Product and restore of an active Product are idempotent no-ops;
- restore re-validates stored name/category through `AlcoholPolicy.require_product_allowed`;
- `archived_by_alcohol_policy=true` cannot be cleared or restored and returns HTTP 409;
- `product_archived` or `product_restored` is appended in the same transaction as the Product state change;
- audit failure rolls back the state change;
- existing Product and Recipe response shapes remain stable because archive state is isolated in dedicated DTOs.

## Dish archive boundary — TH-0109

`DishArchiveService` is authoritative for Dish soft archive and restoration.

### Projection

- the established `GET /api/v1/dishes` contract remains active-only and unchanged;
- `GET /api/v1/dishes/archive` requires preparation access and uses a separate archive response schema;
- the archive projection contains Dish identity/display fields, primary Recipe name, `is_archived`, and `archived_by_alcohol_policy`;
- Dish selectors and catalogue readiness continue to consume only active rows;
- Frontend displays Backend state and does not infer restore eligibility.

### Mutation

- archive and restore target the Dish by ID under `SELECT ... FOR UPDATE`;
- archive changes only `is_archived` and never deletes the Dish, Recipe variants, roles, or historical MealSlot links;
- repeated archive of an archived Dish and restore of an active Dish are idempotent no-ops;
- restore re-validates the stored name through `AlcoholPolicy.require_dish_name_allowed`;
- `archived_by_alcohol_policy=true` cannot be cleared or restored and returns HTTP 409;
- `dish_archived` or `dish_restored` is appended in the same transaction as the Dish state change;
- audit failure rolls back the state change;
- existing Dish and Recipe response shapes remain stable because archive state is isolated in dedicated DTOs.

## Session administration boundary — TH-0107

`SessionAdministrationService` remains authoritative for own-session projection and individual revocation.

- the current login is matched by hashing the HttpOnly cookie server-side;
- only matching active non-expired rows are returned;
- response fields are ID and timestamps plus current marker;
- token/cookie/header/IP/device/user-agent/fingerprint/location data are never serialized;
- unrelated/revoked/expired/unknown IDs return 404;
- current-login revocation returns 409 and ordinary logout remains its termination path;
- revocation and `account_session_revoked` commit or roll back together.

## Project ownership and access boundary

`ProjectAccessPolicy` remains authoritative for Project, Menu/MealSlot, preparation, Shopping, Checklist, Equipment, Documents, contacts, settings, status, and deletion routes.

- `Project.owner_user_id` identifies one owner;
- `ProjectInstructor(project_id, user_id)` stores additional instructors;
- unrelated users receive HTTP 404 for direct and nested paths;
- visible users receive HTTP 403 for role-forbidden actions;
- completed-Project writes receive HTTP 409;
- Frontend capability projection guides controls but never replaces Backend checks;
- ownership transfer and team/status/deletion audit share owning transactions;
- future `Копировать проект` creates a new identity from completed history and remains separate.

## Actor-aware audit boundary

- `AuditEvent` is append-only with actor snapshots and bounded safe JSON;
- business mutation and AuditEvent share the owning transaction;
- no-op writes create no event;
- Product and Dish archive actions store bounded before/after snapshots and `policy_locked` context;
- passwords, hashes, credentials, cookies, tokens, headers, contacts, request bodies, source CSV bodies, document contents, provider secrets, and device/network metadata are excluded;
- automatic ORM-wide auditing remains rejected.

## Audit CSV export boundary — TH-0106

- `AuditService` owns shared list/export filters;
- the Audit router remains Administrator-only;
- export is deterministic UTF-8 CSV over persisted sanitized fields;
- formula-like spreadsheet cells are neutralized;
- exports above 10,000 matching events return HTTP 422;
- export creates no AuditEvent;
- retention/SIEM/scheduling/diagnostics/undo/replay remain separate future boundaries.

## Runtime and release boundary

Development starts with `docker compose up -d --build`; operators use `docker-compose.release.yml`. Frontend, Backend, PostgreSQL, and Redis run locally.

- current post-release Alembic head: `h10023`;
- TH-0106 through TH-0109 added no migrations;
- immutable `v0.1.0` remains at SHA `8bcc2d2d9414d812d81634330034b15121c8442f` and released head `h10021`;
- PostgreSQL backup/restore, clean release-stack startup, restart persistence, and exact-head gates verify candidates;
- multi-tenancy and microservices remain prohibited.

No post-release product task is active after TH-0109. Retention UI, ownership-aware import UX, session extensions, and `Копировать проект` require separate explicit tasks. See `PRODUCT_SPEC.md` and ADR-012 through ADR-026.
