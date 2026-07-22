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
- Own-session listing and individual revocation extend the existing server-session boundary without device tracking or cross-user administration.

## Access runtime

- one User may own multiple independent server sessions;
- PostgreSQL stores only session-token hashes and session metadata;
- Backend resolves the current persisted User on every authorized request;
- deactivation revokes sessions and removes runtime Project access without deleting historical membership;
- protected HTTP 401 responses clear stale Frontend identity centrally;
- the header exposes the current user and opens `/account`;
- `/account` projects only the current User's active sessions;
- account recovery, global sign-out, Administrator session administration, session cleanup, and retention remain future capabilities.

## Session administration boundary — TH-0107

`SessionAdministrationService` is authoritative for own-session projection and individual revocation.

### Projection

- routes remain under authenticated `/api/v1/account`;
- the current login is matched by hashing the existing HttpOnly cookie server-side;
- only rows with matching `user_id`, `revoked_at IS NULL`, and future `expires_at` are returned;
- response fields are session ID, created-at, last-seen-at, expires-at, and current marker;
- raw tokens, token hashes, cookies, authorization headers, IP addresses, user agents, device names, fingerprints, and locations are never serialized;
- Frontend renders the Backend projection and makes no ownership/current-login decision.

### Individual revocation

- target selection is constrained by current `user_id`, active state, and non-expiry before row locking;
- unrelated, revoked, expired, and unknown IDs share the same HTTP 404 result;
- current-login revocation returns HTTP 409 and ordinary logout remains its termination path;
- the target row's `revoked_at` and semantic `account_session_revoked` AuditEvent commit or roll back together;
- the event contains target session ID, active/revoked state, and sanitizer-safe `current_login_preserved` only;
- no cleanup, deletion, background task, device inference, global revoke-all, or cross-user administration is introduced.

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

Ownership transfer locks the Project and involved users, removes the new owner from additional membership, adds the previous owner as an additional instructor, changes `owner_user_id`, appends `project_owner_transferred`, and commits or rolls back as one unit.

## Project contact and completion boundaries

- `/account` owns only the current user's profile, own sessions, password change, and logout;
- the club-wide contact API is removed;
- Project team reads expose owner and additional instructors only after Project visibility is established;
- Project-scoped vCard download repeats the same access and membership checks;
- active members expose approved contact actions; inactive historical members expose identity but no actions;
- Project audit payloads never contain phone numbers or social URLs;
- `completed` is terminal, hidden from catalogue by default, and read-only except owner/Administrator deletion;
- future `Копировать проект` creates a new identity from a completed template and remains a separate task.

## Actor-aware audit boundary

- `AuditEvent` remains append-only with actor snapshots and bounded safe JSON;
- business mutation and AuditEvent share the owning transaction for audited writes;
- no-op writes create no event;
- audit failure rolls back pending domain mutations, including individual session revocation;
- passwords, hashes, credentials, cookies, session tokens, authorization data, phone/social contacts, request bodies, source CSV bodies, generated document contents, provider secrets, and device/network metadata are excluded;
- automatic ORM-wide auditing remains rejected.

## Audit CSV export boundary — TH-0106

`AuditService` owns one filter builder used by paginated Audit list queries and bounded export queries. The Audit router remains included under the centralized Administrator dependency.

- supported filters: actor user ID, entity type, entity ID, semantic action, created-from, and created-to;
- `/api/v1/audit/events/export.csv` returns a read-only UTF-8 CSV projection;
- columns contain only persisted actor snapshots, semantic identity, timestamp, and sanitized before/after/context JSON;
- JSON cells use deterministic key ordering and formula-like spreadsheet cells are neutralized;
- exports above 10,000 matching events return HTTP 422 and require narrower filters;
- export creates no AuditEvent and therefore cannot recursively mutate the journal;
- retention deletion/cleanup, SIEM delivery, scheduling, diagnostics, undo, and replay remain separate future boundaries.

## Runtime and release boundary

Development starts with `docker compose up -d --build`; operators use `docker-compose.release.yml`. Frontend, Backend, PostgreSQL, and Redis run locally.

- current post-release Alembic head: `h10023`;
- TH-0106 and TH-0107 added no migrations;
- immutable `v0.1.0` tag remains at release SHA `8bcc2d2d9414d812d81634330034b15121c8442f` and released head `h10021`;
- PostgreSQL backup/restore, clean release-stack startup, restart persistence, and exact-head gates verify the current candidate;
- multi-tenancy and microservices remain prohibited.

No post-release product task is active after TH-0107. See `PRODUCT_SPEC.md` and ADR-012 through ADR-026.
