# TourHub Current Architecture

Status: Active

Last updated: 2026-07-24

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
- Ownership-aware Recipe CSV import is Backend-owned orchestration over existing parser, alcohol validation, ownership fields, and transaction-owned audit.
- Copy Project is a dedicated Backend-owned transaction that creates a new identity from completed history without reopening the source.

## Copy Project boundary — TH-0111

`ProjectCopyService` is authoritative for source eligibility, destination identity, copy matrix, dependency checks, warnings, and audit.

### Source and authorization

- the source is loaded through centralized Project visibility masking;
- only the source owner or an Administrator may copy it;
- source status must be `completed`;
- additional instructors receive role-forbidden behavior and unrelated users retain existence masking;
- the source Project and its relationships are read-only inputs to the operation.

### Destination transaction

- ordinary Project creation values are validated again in Backend;
- destination receives a new Project ID, `draft` status, and the authenticated actor as owner;
- a new MealPlan/day/MealSlot graph is built from destination parameters;
- matching source slot assignments are copied only when Dish is active and selected Recipe remains eligible for the destination generation mode/current actor;
- invalid assignments become bounded warnings rather than source mutations;
- owner/team membership, derived purchasing/checklist/equipment/readiness/document state, timestamps, and history are excluded;
- destination persistence and `project_copied` AuditEvent commit or roll back together.

### Frontend

- copy entry is shown only for completed Projects with projected owner/Administrator capability;
- the ordinary Project form is reused with source values as editable defaults;
- the UI prevents a second submission while the first non-idempotent request is pending;
- successful navigation carries only the bounded Backend result for presentation on the destination page;
- real-Chrome acceptance verifies edited payloads, one POST, source immutability, destination navigation, warnings, and mobile overflow.

## Ownership-aware CSV import boundary — TH-0110

`OwnershipAwareCatalogImportService` remains authoritative for Recipe ownership selection and preview/apply binding.

- Product preview/apply remain club-wide and CSV headers remain unchanged;
- legacy Recipe apply without ownership/token remains a fully validated CLUB import;
- preview returns a fingerprint bound to actor ID, kind, scope, and exact CSV content;
- apply re-runs validation and rejects changed content/scope/token before persistence;
- PERSONAL creates current-user-owned draft Recipes and CLUB creates published ownerless Recipes;
- components/notes and `catalog_import_applied` audit share one transaction;
- source CSV bodies and preview tokens are never persisted in audit.

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

`ProjectAccessPolicy` remains authoritative for Project, Menu/MealSlot, preparation, Shopping, Checklist, Equipment, Documents, contacts, settings, status, deletion, and copy visibility.

- `Project.owner_user_id` identifies one owner;
- `ProjectInstructor(project_id, user_id)` stores additional instructors;
- unrelated users receive HTTP 404 for direct and nested paths;
- visible users receive HTTP 403 for role-forbidden actions;
- completed-Project mutation routes receive HTTP 409, while the separate copy operation creates a new identity;
- Frontend capability projection guides controls but never replaces Backend checks.

## Actor-aware audit boundary

- `AuditEvent` is append-only with actor snapshots and bounded safe JSON;
- business mutation and AuditEvent share the owning transaction;
- no-op writes create no event;
- `project_copied` stores bounded source/destination IDs and copied/skipped counts, not a full menu snapshot;
- Product/Dish archive actions store bounded lifecycle snapshots;
- catalogue import audit stores kind/count summaries and excludes source CSV body and preview token;
- passwords, hashes, credentials, cookies, tokens, headers, contacts, request bodies, document contents, provider secrets, and device/network metadata are excluded;
- automatic ORM-wide auditing remains rejected.

## Runtime and release boundary

Development starts with `docker compose up -d --build`; operators use `docker-compose.release.yml`. Frontend, Backend, PostgreSQL, and Redis run locally.

- current post-release Alembic head: `h10023`;
- TH-0106 through TH-0111 added no migrations;
- immutable `v0.1.0` remains at SHA `8bcc2d2d9414d812d81634330034b15121c8442f` and released head `h10021`;
- PostgreSQL backup/restore, clean release-stack startup, restart persistence, and exact-head gates verify candidates;
- multi-tenancy and microservices remain prohibited.

No post-release product task is active after TH-0111. Retention UI, session extensions, notification providers, richer Recipe metadata, and reusable team templates require separate explicit tasks. See `PRODUCT_SPEC.md` and ADR-012 through ADR-026.
