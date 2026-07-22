# TourHub — PROJECT_CONTEXT

Version: 0.1.0

Last update: 2026-07-22

Status: Project ownership, team-scoped access, and Project contacts delivered — TH-0105

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
  → Project creation with creator ownership
  → Optional additional Project instructors
  → Project-scoped visibility and contacts
  → Menu generation and manual editing by owner/Administrator
  → read-only Menu for additional instructors
  → Shopping, Checklist, Equipment, and Documents collaboration
  → terminal completed Project history
  → Actor-aware operational accountability
```

The first release remains tagged `v0.1.0` at released Alembic head `h10021`. Current post-release development is complete through TH-0105 at `h10023`.

## 3. Architecture

TourHub remains a modular monolith using React/TypeScript/Vite/Material UI/TanStack Query on the Frontend and Python 3.13/FastAPI/SQLAlchemy/Alembic/PostgreSQL on the Backend.

### Frontend responsibilities

- present responsive Project catalogue/workspace/account/settings surfaces;
- render Backend-projected Project capabilities;
- hide completed Projects by default while allowing an explicit completed filter;
- present Menu and operational modules in read-only or writable mode;
- display Project-scoped team contact actions;
- never make authorization decisions independently of Backend policy.

### Backend responsibilities

- persist identity, Project owner/team membership, catalogue, preparation, documents, and audit state;
- enforce `ProjectAccessPolicy` on every Project-scoped route;
- mask unrelated Projects as 404;
- reject role-forbidden actions as 403 and completed-Project writes as 409;
- transact team changes, ownership transfer, status changes, deletion, and semantic AuditEvents together;
- normalize contact profiles and expose contacts only through a visible Project team;
- preserve the immutable release-tag contract separately from current post-release migrations.

## 4. Identity and Project access

### Global identity

- one User may own multiple server sessions;
- one User has one global role;
- active Administrators retain site-wide Project visibility;
- deactivation revokes sessions and also removes runtime Project access without deleting historical Project membership.

### Project responsibilities

- every Project has one owner through `owner_user_id`;
- a Project may have any number of `ProjectInstructor` rows;
- owner and additional-instructor membership are mutually exclusive;
- Administrators may be explicitly added to the team when participating as instructors;
- ownership transfer makes the previous owner an additional instructor and removes the new owner from that set.

### Capability matrix

- owner/Administrator: manage Project parameters, Menu, preparation, team, ownership, completion, and deletion; operate all modules;
- additional instructor: view Project/Menu and operate Shopping, Checklist, Equipment, Documents, and Project contacts; no Menu or Project/team-setting writes;
- completed Project: readable/downloadable only; owner/Administrator may delete it;
- outsider: no list result and 404 on direct Project-scoped access.

## 5. Project contacts and personal account

`/account` contains the current user's editable FIO/contact profile, read-only email, password change, and logout. It no longer exposes a club-wide contact directory.

The Project overview returns only the owner and additional instructors after Project visibility is established. Active members expose mail, `tel:`, Telegram, MAX, VK, and Project-scoped vCard actions. Inactive historical members remain identifiable but contact actions are unavailable.

## 6. Data and migrations

- `h10022` adds optional User phone/Telegram/MAX/VK fields;
- `h10023` adds `projects.owner_user_id` and `project_instructors`;
- existing Project owners are backfilled from the earliest trustworthy `project_created` AuditEvent, with first-Administrator fallback;
- current post-release Alembic has one head at `h10023`;
- immutable `v0.1.0` remains fixed at released head `h10021`.

## 7. Audit and notification boundary

Semantic Project-team actions include instructor add/remove, ownership transfer, status change, and deletion. Events contain bounded IDs, names, roles, and state metadata only; contact values, credentials, tokens, arbitrary request bodies, and provider details are excluded.

`ProjectTeamNotificationService` exists as a no-op boundary for future email, Telegram, and MAX notifications. No message, queue item, retry record, or delivery attempt is created today.

## 8. Current active work and immediate sequence

- TH-0061.5 remains operational maintenance for the completed menu rules engine.
- TH-0105 is complete.
- No later product task is active automatically.
- `Копировать проект` is explicitly preserved in the roadmap as a required future Product Owner-selected task.

## 9. Development rules

- Do not invent missing business requirements.
- Do not add multi-tenancy or microservices.
- Do not move authorization or business decisions into React.
- Apply Project access to every direct and nested route, not only catalogue filtering.
- Do not implement ORM-wide automatic auditing.
- Do not reopen completed Projects; future copying creates a new Project identity.
- One logical task is squash-merged to `main`.
- Documentation, task state, roadmap, and technical debt are updated with code.
