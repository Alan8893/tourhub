# TourHub — PROJECT_CONTEXT

Version: 0.1.0

Last update: 2026-07-22

Status: Post-release development complete through TH-0108; no next product task selected

## 1. Product boundary

TourHub is a local ERP application for one tourist club.

- One installation represents one club.
- Multi-tenant support and microservices are prohibited.
- Registration is invitation-only after one-time Administrator bootstrap.
- Global User roles remain singular: Administrator, Instructor, or Verified Instructor.
- Project owner and additional instructor are Project-scoped responsibilities, not additional global roles.
- Alcohol is prohibited without exceptions through one Backend policy.
- Paid or externally hosted runtime services are not used.

The approved target scope is defined in `PRODUCT_SPEC.md`. Current behavior is defined by code, tests, Product Acceptance/Release Readiness evidence, `PROJECT_STATUS.md`, `ARCHITECTURE_CURRENT.md`, `DOMAIN_CURRENT.md`, and accepted ADRs.

## 2. Current product workflow

```text
Administrator bootstrap and invitations
  → Personal account/contact profile and own sessions
  → Project creation with creator ownership and optional additional instructors
  → Project-scoped visibility and contacts
  → Menu generation and preparation collaboration
  → Shopping, Checklist, Equipment, and Documents
  → terminal completed Project history
  → actor-aware operational accountability and Administrator CSV review
  → active Product catalogue with explicit soft-archive management
```

The first release remains tagged `v0.1.0` at released Alembic head `h10021`. Current post-release persistence is complete through TH-0108 at one Alembic head `h10023`; TH-0106, TH-0107, and TH-0108 added no migrations.

## 3. Architecture

TourHub remains a modular monolith using React/TypeScript/Vite/Material UI/TanStack Query on the Frontend and Python 3.13/FastAPI/SQLAlchemy/Alembic/PostgreSQL on the Backend.

### Frontend responsibilities

- present responsive Project, account, settings, audit, Recipe, and catalogue surfaces;
- render Backend-projected Project, session, and Product archive capabilities;
- display only active Products for new Recipe component selection;
- open the explicit Product archive-management view and invoke archive/restore operations;
- display policy-lock reasons without inventing restore eligibility;
- never make authorization, ownership, current-login, alcohol-policy, audit-selection, sanitization, or archive-policy decisions independently of Backend.

### Backend responsibilities

- persist identity, server sessions, Project owner/team membership, catalogue, preparation, documents, and audit state;
- enforce session ownership and current-login protection through `SessionAdministrationService`;
- enforce `ProjectAccessPolicy` on every Project-scoped route;
- own active versus archived Product projections;
- lock Product rows and transact archive/restore state plus semantic AuditEvent together;
- re-run `AlcoholPolicy` before Product restoration and permanently respect `archived_by_alcohol_policy`;
- preserve historical Product references and stable existing API contracts;
- own Audit list/export authorization, filters, limits, CSV shape, and formula neutralization;
- preserve the immutable release-tag contract separately from current post-release migrations.

## 4. Product archive boundary — TH-0108

- `GET /api/v1/products` remains active-only and returns the established Product response shape;
- `GET /api/v1/products/archive` is an explicit preparation-authorized projection containing `is_archived` and `archived_by_alcohol_policy`;
- `POST /api/v1/products/{id}/archive` performs soft archive;
- `POST /api/v1/products/{id}/restore` restores only a manually archived Product still accepted by the central policy;
- Product rows are never deleted and existing Recipe component, purchase, checklist, and document history remains valid;
- archive/restore are row-locked, idempotent, and audit-owned by the same transaction;
- audit actions are `product_archived` and `product_restored` with bounded Product snapshots and `policy_locked` context;
- policy-locked Products return 409 on restore and never have their alcohol marker cleared;
- Dish archive management is not part of TH-0108.

## 5. Identity and sessions

- one User may own multiple independent server sessions and one global role;
- active Administrators retain site-wide Project visibility and exclusive Audit access;
- every active User may list only their own active non-expired sessions;
- raw tokens, hashes, cookies, authorization headers, IP/device/user-agent/fingerprint/location data are never returned;
- another owned active session may be revoked by ID while current-login revocation remains ordinary logout;
- global sign-out, cross-user session administration, cleanup, deletion, retention, and tracking metadata remain future work.

## 6. Project access and contacts

- every Project has one owner through `owner_user_id` and may have any number of additional instructors;
- owner and additional-instructor membership are mutually exclusive;
- Administrator, owner, and additional instructor capabilities are Backend-enforced;
- completed Projects are terminal read-only history; owner/Administrator may delete them;
- outsiders receive no catalogue item and 404 on direct Project-scoped access;
- Project team contacts are exposed only after Project visibility is established.

## 7. Audit review and export

`AuditEvent` remains append-only and stores bounded actor snapshots plus sanitized semantic before/after/context JSON. `/api/v1/audit/*` is Administrator-only.

- list and CSV export share Backend filters and a 10,000-row export bound;
- JSON columns are deterministic UTF-8 and spreadsheet formula prefixes are neutralized;
- archive actions record state transitions but no request bodies, credentials, headers, unrelated catalogue contents, or historical document bodies;
- export creates no recursive AuditEvent;
- retention deletion/cleanup, SIEM delivery, scheduling, diagnostics, undo, and replay remain separate future work.

## 8. Data and migrations

- released `v0.1.0`: Alembic `h10021`, SHA `8bcc2d2d9414d812d81634330034b15121c8442f`;
- `h10022` adds optional User contact fields;
- `h10023` adds Project ownership and team membership and remains the single current head;
- Product archive fields predate TH-0108, so TH-0108 requires no persistence change;
- immutable `v0.1.0` remains fixed and is not moved by post-release work.

## 9. Current work boundary

- TH-0061.5 remains operational maintenance for the completed menu rules engine.
- TH-0108 is complete and no post-release product task is active.
- Audit retention UI remains deferred until duration, deletion eligibility, safeguards, and rollback policy are approved.
- Dish archive management and ownership-aware CSV import UX remain separate candidate tasks.
- `Копировать проект` remains a required future Product Owner-selected task.

## 10. Development rules

- Do not invent missing business requirements.
- Do not add multi-tenancy or microservices.
- Do not move authorization or business decisions into React.
- Keep Product archive and alcohol-policy decisions in Backend.
- Keep Audit list/export selection and limits in Backend.
- Do not implement ORM-wide automatic auditing.
- Do not reopen completed Projects; future copying creates a new Project identity.
- One logical task is squash-merged to `main`.
- Documentation, task state, roadmap, and technical debt are updated with code.
