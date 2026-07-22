# TourHub — PROJECT_CONTEXT

Version: 0.1.0

Last update: 2026-07-22

Status: Post-release development complete through TH-0107; no next product task selected

## 1. Product boundary

TourHub is a local ERP application for one tourist club.

- One installation represents one club.
- Multi-tenant support and microservices are prohibited.
- Registration is invitation-only after one-time Administrator bootstrap.
- Global User roles remain singular: Administrator, Instructor, or Verified Instructor.
- Project owner and additional instructor are Project-scoped responsibilities, not additional global roles.
- Alcohol is prohibited without exceptions through one Backend policy.
- Paid or externally hosted runtime services are not used.

The approved target scope is defined in `PRODUCT_SPEC.md`. Current behavior is defined by code, tests, Product Acceptance/Release Readiness evidence, `PROJECT_STATUS.md`, `ARCHITECTURE_CURRENT.md`, `DOMAIN_CURRENT.md`, and ADR-026.

## 2. Current product workflow

```text
Administrator bootstrap and invitations
  → Personal account/contact profile
  → own active-session review and individual revocation
  → Project creation with creator ownership
  → Optional additional Project instructors
  → Project-scoped visibility and contacts
  → Menu generation and manual editing by owner/Administrator
  → read-only Menu for additional instructors
  → Shopping, Checklist, Equipment, and Documents collaboration
  → terminal completed Project history
  → Actor-aware operational accountability
  → Administrator filtered CSV audit review
```

The first release remains tagged `v0.1.0` at released Alembic head `h10021`. Current post-release persistence is complete through TH-0107 at one Alembic head `h10023`; TH-0106 and TH-0107 added no migrations.

## 3. Architecture

TourHub remains a modular monolith using React/TypeScript/Vite/Material UI/TanStack Query on the Frontend and Python 3.13/FastAPI/SQLAlchemy/Alembic/PostgreSQL on the Backend.

### Frontend responsibilities

- present responsive Project catalogue/workspace/account/settings surfaces;
- render Backend-projected Project and session capabilities;
- hide completed Projects by default while allowing an explicit completed filter;
- present Menu and operational modules in read-only or writable mode;
- display Project-scoped contact actions;
- collect Audit filters and start a browser CSV download;
- display the current user's Backend-projected active sessions and invoke individual revocation;
- never make authorization, ownership, current-login, audit-selection, sanitization, or export-limit decisions independently of Backend policy.

### Backend responsibilities

- persist identity, server sessions, Project owner/team membership, catalogue, preparation, documents, and audit state;
- resolve the current persisted User and session token-hash boundary on every authorized request;
- enforce own-session ownership and current-login protection through `SessionAdministrationService`;
- enforce `ProjectAccessPolicy` on every Project-scoped route and mask unrelated Projects as 404;
- reject role-forbidden actions as 403 and completed-Project writes as 409;
- transact team changes, ownership transfer, status changes, deletion, session revocation, and semantic AuditEvents together;
- normalize contact profiles and expose contacts only through a visible Project team;
- own Audit list/export authorization, filters, bounded row limits, deterministic CSV shape, and formula neutralization;
- preserve the immutable release-tag contract separately from current post-release migrations.

## 4. Identity and sessions

- one User may own multiple independent server sessions;
- one User has one global role;
- active Administrators retain site-wide Project visibility and exclusive Audit access;
- deactivation revokes sessions and removes runtime Project access without deleting historical membership;
- every active authenticated User may list only their own active non-expired sessions;
- the current login is identified from the existing HttpOnly cookie and marked server-side;
- session responses contain only ID, created-at, last-seen-at, expires-at, and current marker;
- raw tokens, token hashes, cookies, authorization headers, IP, device, user-agent, fingerprint, and location are never returned;
- another owned active session may be revoked by ID;
- unrelated/revoked/expired/unknown IDs return 404 and current-login revocation returns 409;
- ordinary logout remains the current-login termination path;
- revocation and safe semantic audit share one transaction and rollback boundary;
- audit context uses `current_login_preserved`, which passes the central sanitizer without exposing session/token/cookie fields.

Global sign-out, Administrator cross-user session management, cleanup, deletion, retention, and tracking metadata remain future work.

## 5. Project access and contacts

- every Project has one owner through `owner_user_id` and may have any number of `ProjectInstructor` rows;
- owner and additional-instructor membership are mutually exclusive;
- Administrators may be explicitly added to the team when participating as instructors;
- owner/Administrator may manage Project parameters, Menu, preparation, team, ownership, completion, deletion, and all operational modules while open;
- additional instructors may view Project/Menu and operate Shopping, Checklist, Equipment, Documents, and Project contacts, but may not write Menu or Project/team settings;
- completed Projects are terminal read-only history; owner/Administrator may delete them;
- outsiders receive no catalogue item and 404 on direct Project-scoped access;
- `/account` contains only the current user's profile, own sessions, password change, and logout;
- Project team contacts are exposed only after Project visibility is established.

## 6. Audit review and export

`AuditEvent` remains append-only and stores bounded actor snapshots plus sanitized semantic before/after/context JSON. `/api/v1/audit/*` is Administrator-only.

- list and CSV export share actor, entity type, entity ID, action, created-from, and created-to filters in `AuditService`;
- CSV contains only persisted AuditEvent fields and does not rehydrate protected domain values;
- JSON columns are deterministic UTF-8 text and spreadsheet formula prefixes are neutralized;
- more than 10,000 matching events requires narrower filters;
- export creates no `audit_exported` event and cannot recursively mutate the journal;
- `account_session_revoked` stores target ID, active/revoked state, and `current_login_preserved` only;
- contact values, credentials, tokens, hashes, cookies, arbitrary request bodies, provider details, and device/network metadata are excluded.

## 7. Data and migrations

- `h10022` adds optional User phone/Telegram/MAX/VK fields;
- `h10023` adds `projects.owner_user_id` and `project_instructors`;
- existing Project owners are backfilled from the earliest trustworthy `project_created` AuditEvent, with first-Administrator fallback;
- current post-release Alembic has one head at `h10023`;
- TH-0106 and TH-0107 require no persistence change;
- immutable `v0.1.0` remains fixed at released head `h10021` and release SHA `8bcc2d2d9414d812d81634330034b15121c8442f`.

## 8. Current work boundary

- TH-0061.5 remains operational maintenance for the completed menu rules engine.
- TH-0105, TH-0106, and TH-0107 are complete.
- No post-release product task is active.
- Audit retention UI remains deferred until duration, deletion eligibility, safeguards, and rollback policy are approved.
- Product/Dish archive management and ownership-aware CSV import UX remain separate candidate tasks.
- `Копировать проект` remains a required future Product Owner-selected task.

## 9. Development rules

- Do not invent missing business requirements.
- Do not add multi-tenancy or microservices.
- Do not move authorization or business decisions into React.
- Keep session ownership, current-login detection, and revocation policy in Backend.
- Apply Project access to every direct and nested route.
- Keep Audit list/export selection and limits in Backend.
- Do not implement ORM-wide automatic auditing.
- Do not reopen completed Projects; future copying creates a new Project identity.
- One logical task is squash-merged to `main`.
- Documentation, task state, roadmap, and technical debt are updated with code.
