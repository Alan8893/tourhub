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
- Global User roles remain singular.
- Owner and additional instructor are Project-scoped responsibilities.
- Module visibility remains presentation-only and never grants access.
- Audit CSV export is a Backend-owned read projection over sanitized AuditEvent persistence.

## Access runtime

- one User may own multiple independent server sessions;
- PostgreSQL stores only session-token hashes and session metadata;
- Backend resolves the current persisted User on every authorized request;
- deactivation revokes sessions and removes runtime Project access without deleting historical membership;
- protected HTTP 401 responses clear stale frontend identity centrally;
- the header exposes the current user and opens `/account`;
- account recovery and general session administration remain future capabilities.

## Project ownership and access boundary

### Persistence

- `Project.owner_user_id` identifies exactly one owner in production;
- `ProjectInstructor(project_id, user_id)` stores any number of additional instructors;
- `added_by_user_id` and `created_at` preserve bounded membership provenance;
- owner and additional-instructor membership are mutually exclusive by service invariant;
- Administrators may be explicitly included as Project instructors without changing their global role;
- `h10023` backfills existing owners from the earliest trustworthy `project_created` AuditEvent, then falls back to the first Administrator.

### Central policy

`ProjectAccessPolicy` is authoritative for Project, Menu/MealSlot, preparation status/orchestration, Shopping/PurchaseList, Checklist, Equipment, Documents, team contacts, settings, status, and deletion routes.

- unrelated users receive HTTP 404 for direct and nested Project paths;
- visible users receive HTTP 403 for role-forbidden actions;
- completed-Project writes receive HTTP 409;
- Frontend capability projection guides controls but never replaces Backend checks.

### Capabilities

- Administrator: site-wide Project visibility and owner-equivalent management while a Project is open;
- owner: manage Project parameters, Menu, preparation, team, ownership, completion, deletion, and every operational module;
- additional instructor: view Project/Menu; operate Shopping, Checklist, Equipment, Documents, and Project contacts; no Menu or Project/team-setting writes;
- completed Project: terminal read-only history; owner/Administrator may delete it;
- inactive owner/member: membership retained, access denied until reactivation.

### Ownership transfer

Ownership transfer locks the Project and involved users, removes the new owner from additional membership, adds the previous owner as an additional instructor, changes `owner_user_id`, appends `project_owner_transferred`, and commits or rolls back as one unit.

## Project contact boundary

- `/account` owns only the current user's profile, password change, and logout;
- the club-wide contact API is removed;
- Project team reads expose owner and additional instructors only after Project visibility is established;
- Project-scoped vCard download repeats the same access and membership checks;
- active members expose mail, phone, Telegram, MAX, and VK actions;
- inactive historical members expose identity but no contact actions;
- Project audit payloads never contain phone numbers or social URLs.

## Completed Project boundary

- `completed` is terminal in the current model;
- completed Projects are hidden from the catalogue by default;
- reads and document downloads remain available to authorized users;
- all operational, Menu, settings, team, transfer, and status writes are rejected;
- no reopen endpoint exists;
- future `Копировать проект` creates a new identity from a completed template and remains a separate task.

## Project-team notification boundary

`ProjectTeamNotificationService` defines add/remove/ownership-transfer callbacks. TH-0105 uses `NoOpProjectTeamNotificationService`; no email, Telegram, MAX, queue, retry, delivery history, or provider call occurs. Future delivery must implement this boundary explicitly.

## Actor-aware audit boundary

- `AuditEvent` remains append-only with actor snapshots and bounded safe JSON;
- business mutation and AuditEvent share the owning transaction for audited writes;
- no-op writes create no event;
- audit failure rolls back pending domain mutations;
- passwords, hashes, credentials, cookies, sessions, tokens, authorization data, phone/social contacts, request bodies, source CSV bodies, generated document contents, and provider secrets are excluded;
- automatic ORM-wide auditing remains rejected.

## Audit CSV export boundary — TH-0106

`AuditService` owns one filter builder used by paginated Audit list queries and bounded export queries. The Audit router remains included under the centralized Administrator dependency.

- supported filters: actor user ID, entity type, entity ID, semantic action, created-from, and created-to;
- `/api/v1/audit/events/export.csv` returns a read-only UTF-8 CSV projection;
- export rows are ordered by descending AuditEvent ID, matching list chronology;
- columns contain only persisted actor snapshots, semantic identity, timestamp, and sanitized before/after/context JSON;
- JSON cells use deterministic key ordering and compact UTF-8 serialization;
- formula-like spreadsheet cells are prefixed with an apostrophe;
- exports above 10,000 matching events return HTTP 422 and require narrower filters;
- export creates no AuditEvent and therefore cannot recursively mutate the journal;
- retention deletion/cleanup, SIEM delivery, scheduling, diagnostics, undo, and replay remain separate future boundaries;
- TH-0106 adds no migration.

## Recipe, catalogue, documents, and mail boundaries

Existing Recipe ownership, Dish variants, exact assignment snapshots, alcohol policy, catalogue import, shopping/equipment recalculation, consolidated exports, and mail-delivery boundaries remain unchanged except that Project-scoped routes require `ProjectAccessPolicy` authorization.

Document generation remains non-persisted. Authorized Project members may download approved documents, including from a completed Project, while generation audit stores only safe document metadata.

## Runtime and release boundary

Development starts with `docker compose up -d --build`; operators use `docker-compose.release.yml`. Frontend, Backend, PostgreSQL, and Redis run locally.

- current post-release Alembic head: `h10023`;
- immutable `v0.1.0` tag remains at release SHA `8bcc2d2d9414d812d81634330034b15121c8442f` and released head `h10021`;
- PostgreSQL backup/restore, clean release-stack startup, restart persistence, and exact-head gates verify the current candidate;
- multi-tenancy and microservices remain prohibited.

See `PRODUCT_SPEC.md` and ADR-012 through ADR-026.
