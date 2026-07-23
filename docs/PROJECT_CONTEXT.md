# TourHub — PROJECT_CONTEXT

Version: 0.1.0

Last update: 2026-07-22

Status: Post-release development complete through TH-0110; no next product task selected

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
  → active Product and Dish catalogues with explicit soft-archive management
  → Product CSV import and CLUB/PERSONAL Recipe CSV import
```

The first release remains tagged `v0.1.0` at released Alembic head `h10021`. Current post-release persistence is complete through TH-0110 at one Alembic head `h10023`; TH-0106 through TH-0110 added no migrations.

## 3. Architecture

TourHub remains a modular monolith using React/TypeScript/Vite/Material UI/TanStack Query on the Frontend and Python 3.13/FastAPI/SQLAlchemy/Alembic/PostgreSQL on the Backend.

### Frontend responsibilities

- present responsive Project, account, settings, audit, Recipe, catalogue, and import surfaces;
- render Backend-projected Project, session, Product archive, Dish archive, and import capabilities;
- display only active Products/Dishes for new selection;
- collect one explicit CLUB/PERSONAL target for Recipe CSV import;
- return the Backend preview token unchanged on apply and reset preview when CSV or scope changes;
- display policy and ownership outcomes without inventing authorization or lifecycle decisions;
- never make authorization, ownership, current-login, alcohol-policy, audit-selection, sanitization, archive-policy, or import-validation decisions independently of Backend.

### Backend responsibilities

- persist identity, sessions, Project team, Recipe ownership/lifecycle, catalogue, preparation, documents, and audit state;
- enforce preparation and Project access centrally;
- own active/archive catalogue projections and lifecycle transactions;
- own CSV parsing, duplicate/reference validation, central alcohol policy, Recipe ownership creation, preview token verification, and all-or-nothing import transaction;
- preserve Product import compatibility and stable existing API contracts;
- keep Audit list/export filters and safe semantic mutation audit in Backend;
- preserve the immutable release-tag contract separately from current post-release migrations.

## 4. Ownership-aware Recipe CSV import — TH-0110

- Product CSV import remains club-wide and unchanged;
- Recipe preview/apply require preparation access;
- the UI sends one explicit `club` or `personal` scope for the whole Recipe import;
- PERSONAL creates `scope=personal`, `owner_user_id=current actor`, and `lifecycle_status=draft`;
- CLUB creates `scope=club`, no owner, and `lifecycle_status=published`;
- preview reuses existing parser and alcohol validation, then returns an actor/content/scope-bound token;
- ownership-aware apply revalidates the CSV and rejects missing/mismatched token, content, or scope with HTTP 409 before persistence;
- legacy apply without ownership/token remains compatible as validated CLUB import;
- components and notes share the new Recipe identity and add no independent ownership;
- import state and bounded actor-aware audit commit or roll back together;
- source CSV bodies and preview tokens are excluded from audit persistence.

## 5. Product and Dish archive boundary

- default Product and Dish lists remain active-only and preserve established response contracts;
- explicit preparation-authorized archive projections expose lifecycle and policy-lock state;
- archive is soft, history is preserved, restore re-runs central alcohol policy, and policy-locked rows remain non-restorable;
- row lock, idempotency, state, and semantic audit share the owning transaction.

## 6. Identity, sessions, and Project access

- one User may own multiple independent server sessions and one global role;
- every Project has one owner and may have additional instructors;
- `ProjectAccessPolicy` controls Project-scoped preparation, contacts, shopping, equipment, documents, status, and deletion;
- completed Projects remain terminal read-only history;
- own-session projection excludes tokens and tracking metadata;
- global sign-out, cross-user session administration, cleanup, deletion, retention, and tracking metadata remain future work.

## 7. Audit review and export

`AuditEvent` remains append-only and stores bounded actor snapshots plus sanitized semantic before/after/context JSON. `/api/v1/audit/*` is Administrator-only.

- list and CSV export share Backend filters and a 10,000-row export bound;
- JSON columns are deterministic UTF-8 and spreadsheet formula prefixes are neutralized;
- archive/import actions exclude request bodies, credentials, headers, source CSV bodies, preview tokens, unrelated catalogue data, and document bodies;
- export creates no recursive AuditEvent;
- retention deletion/cleanup, SIEM delivery, scheduling, diagnostics, undo, and replay remain separate future work.

## 8. Data and migrations

- released `v0.1.0`: Alembic `h10021`, SHA `8bcc2d2d9414d812d81634330034b15121c8442f`;
- `h10022` adds optional User contact fields;
- `h10023` adds Project ownership and team membership and remains the single current head;
- Product/Dish archive fields and Recipe ownership fields predate TH-0108 through TH-0110, so no new persistence change was required;
- immutable `v0.1.0` remains fixed and is not moved by post-release work.

## 9. Current work boundary

- TH-0061.5 remains operational maintenance for the completed menu rules engine.
- TH-0110 is complete and no post-release product task is active.
- Audit retention UI remains deferred until duration, deletion eligibility, safeguards, and rollback policy are approved.
- `Копировать проект` remains a required future Product Owner-selected task.
- Session extensions and Project-team notification providers remain separate tasks.

## 10. Development rules

- Do not invent missing business requirements.
- Do not add multi-tenancy or microservices.
- Do not move authorization or business decisions into React.
- Keep import parsing, ownership, token verification, and transaction policy in Backend.
- Keep Product/Dish archive and alcohol-policy decisions in Backend.
- Keep Audit list/export selection and limits in Backend.
- Do not implement ORM-wide automatic auditing.
- Do not reopen completed Projects; future copying creates a new Project identity.
- One logical task is squash-merged to `main`.
- Documentation, task state, roadmap, and technical debt are updated with code.
