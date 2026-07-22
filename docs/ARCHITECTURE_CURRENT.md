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
- Ownership-aware Recipe CSV import is a Backend-owned orchestration over the existing parser, alcohol validation, Recipe ownership fields, and transaction-owned audit.

## Ownership-aware CSV import boundary — TH-0110

`OwnershipAwareCatalogImportService` is authoritative for Recipe ownership selection and preview/apply binding.

### Stable compatibility

- Product preview/apply remain club-wide and continue through the established alcohol-aware import service;
- CSV headers and row format remain unchanged;
- legacy Recipe apply without ownership/token remains a fully validated CLUB import;
- existing duplicate, existing-name, Product reference, component, note, and alcohol-policy rules are reused rather than duplicated.

### Preview

- `/api/v1/catalog-import/preview` requires preparation access;
- Recipe preview accepts one optional API ownership scope, resolved as CLUB for compatibility;
- the current UI always sends explicit `club` or `personal`;
- response includes resolved ownership scope and a SHA-256 fingerprint bound to actor ID, import kind, ownership scope, and exact CSV content;
- preview creates no Recipe and no AuditEvent.

### Apply

- ownership-aware Recipe apply re-runs full validation before any write;
- explicit scope requires the matching preview token;
- changed content/scope/token returns HTTP 409 before persistence or audit;
- PERSONAL creates current-user-owned draft Recipes;
- CLUB creates published club Recipes with no owner;
- components and deduplicated notes are persisted under the new Recipe identities;
- state and `catalog_import_applied` audit share one commit/rollback boundary;
- source CSV bodies and preview tokens are never persisted in audit.

### Frontend

- ownership selection and explanation are presentation of Backend-supported targets, not authorization;
- changing kind, CSV content, or scope clears preview;
- apply is enabled only for a valid matching preview;
- real-Chrome acceptance verifies payloads, invalidation, success state, and mobile overflow.

## Product and Dish archive boundaries

- established active-list contracts remain unchanged;
- explicit archive projections require preparation access;
- archive/restore use row locks, soft lifecycle, idempotency, central alcohol-policy revalidation, permanent policy lock, and transaction-owned semantic audit;
- Product, Dish, Recipe variant, role, MealSlot, shopping, checklist, equipment, and document history is preserved.

## Access runtime

- one User may own multiple independent server sessions;
- PostgreSQL stores only session-token hashes and session metadata;
- Backend resolves the persisted User on every authorized request;
- deactivation revokes sessions and removes runtime Project access without deleting history;
- `/account` projects only the current User's active sessions;
- recovery, global sign-out, Administrator session administration, cleanup, and retention remain future work.

## Project ownership and access boundary

`ProjectAccessPolicy` remains authoritative for Project, Menu/MealSlot, preparation, Shopping, Checklist, Equipment, Documents, contacts, settings, status, and deletion routes.

- `Project.owner_user_id` identifies one owner;
- `ProjectInstructor(project_id, user_id)` stores additional instructors;
- unrelated users receive HTTP 404 for direct and nested paths;
- visible users receive HTTP 403 for role-forbidden actions;
- completed-Project writes receive HTTP 409;
- Frontend capability projection guides controls but never replaces Backend checks;
- future `Копировать проект` creates a new identity from completed history and remains separate.

## Actor-aware audit boundary

- `AuditEvent` is append-only with actor snapshots and bounded safe JSON;
- business mutation and AuditEvent share the owning transaction;
- no-op writes create no event;
- Product/Dish archive actions store bounded lifecycle snapshots;
- catalogue import audit stores kind/count summaries and excludes source CSV body and preview token;
- passwords, hashes, credentials, cookies, tokens, headers, contacts, request bodies, document contents, provider secrets, and device/network metadata are excluded;
- automatic ORM-wide auditing remains rejected.

## Runtime and release boundary

Development starts with `docker compose up -d --build`; operators use `docker-compose.release.yml`. Frontend, Backend, PostgreSQL, and Redis run locally.

- current post-release Alembic head: `h10023`;
- TH-0106 through TH-0110 added no migrations;
- immutable `v0.1.0` remains at SHA `8bcc2d2d9414d812d81634330034b15121c8442f` and released head `h10021`;
- PostgreSQL backup/restore, clean release-stack startup, restart persistence, and exact-head gates verify candidates;
- multi-tenancy and microservices remain prohibited.

No post-release product task is active after TH-0110. Retention UI, session extensions, notification providers, richer Recipe metadata, and `Копировать проект` require separate explicit tasks. See `PRODUCT_SPEC.md` and ADR-012 through ADR-026.
