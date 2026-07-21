# TourHub — PROJECT_CONTEXT

Version: 0.1.0

Last update: 2026-07-21

Status: Post-release personal account and club contacts delivered — TH-0104

## 1. Product boundary

TourHub is a local ERP application for one tourist club.

- One installation represents one club.
- Multi-tenant support is prohibited.
- The runtime supports multiple invited users inside the same club.
- Registration is invitation-only after one-time Administrator bootstrap.
- Approved roles are Administrator, Instructor, and Verified Instructor.
- Authenticated users may maintain contact profiles and view active club contacts.
- Trip calculations still use participant count; separate trip-participant profiles are not implemented.
- Alcohol is prohibited without exceptions through one Backend policy.
- Paid or externally hosted runtime services are not used.

The approved target scope is defined in `PRODUCT_SPEC.md`. The current state is defined by code, tests, Product Acceptance/Release Readiness evidence, `PROJECT_STATUS.md`, `ARCHITECTURE_CURRENT.md`, and `DOMAIN_CURRENT.md`.

## 2. Released product workflow

```text
Administrator bootstrap and invitations
  → Personal account and active club contacts
  → Project
  → Menu generation and manual MealSlot editing
  → Club and personal Recipes
  → Recipe publication and moderation
  → automatic published Recipe synchronization into Dishes
  → explicit Dish generator-role setup
  → Dish Recipe variants and project generation modes
  → Shopping and packaging
  → Equipment
  → Complete PDF, Excel, compatibility files, and ZIP
  → Actor-aware operational accountability
  → Central alcohol prohibition
  → Product acceptance and feature freeze
  → Final migration and release readiness
```

The complete first-release sequence is delivered through TH-0093 and tagged `v0.1.0`. TH-0095 through TH-0103 deliver workspace, catalogue, synchronization, and semantic audit improvements. TH-0104 adds authenticated personal profiles, active-club contact sharing, vCard download, safe password change, and account-owned logout.

## 3. Architecture

TourHub remains a modular monolith.

### Frontend

- React;
- TypeScript;
- Vite;
- Material UI;
- TanStack Query;
- React Router.

Frontend owns presentation, responsive navigation, personal-account forms, contact actions, Project workspace routing, Product create/edit state, Dish generator-readiness presentation, query invalidation, safe AuditEvent rendering/filtering, and download controls. It does not own profile normalization, password verification, session revocation, business validation, generation rules, authorization, calculations, or audit sanitization.

### Backend

- Python 3.13;
- FastAPI;
- SQLAlchemy 2.x;
- Alembic;
- Pydantic v2;
- PostgreSQL 18 in the release runtime;
- Redis configuration;
- deterministic identity, calculation, document, audit, and catalogue-policy boundaries.

Backend owns validation, profile normalization, persistence, identity/authorization, invitation lifecycle, password hashing, session revocation, contact visibility, Product policy, Recipe ownership/lifecycle, published Recipe-to-Dish synchronization, Dish variant selection, menu generation, manual MealSlot mutation, catalogue import, central alcohol policy, shopping/checklist/equipment recalculation, mail boundaries, document generation, and semantic audit rules in owning transactions.

### Runtime

Development starts with:

```bash
docker compose up -d --build
```

The operator path uses `docker-compose.release.yml`. Frontend, Backend, PostgreSQL, and Redis run locally. PostgreSQL and Redis remain internal to the release network. Redis is available but no released business workflow depends on it.

## 4. Current baseline

### Access, users, and personal accounts

- one-time Administrator bootstrap and invitation-only registration;
- password hashing and server-owned HttpOnly sessions;
- working SMTP invitation delivery with manual fallback;
- roles, activation controls, optimistic user versions, and last-active-Administrator protection;
- preparation access for all approved active roles;
- Administrator-only settings, invitations, user administration, mail operations, and audit reads;
- multiple logins, current-role resolution, deactivation revocation, protected-401 handling, exact route return, and visible role;
- `/account` is available to every authenticated active user;
- existing `display_name` is the single FIO field and email remains the immutable login identifier;
- optional phone, Telegram, MAX, and VK values are normalized by Backend;
- social profile values accept a handle or an approved HTTPS profile URL;
- all authenticated active users may list active club contacts;
- `mailto:`, `tel:`, approved social links, and vCard download support contact use on phones;
- password change requires the current password, preserves the current login, and revokes all other active logins;
- logout moved from the global header into the personal account page;
- avatars, public profiles, email/phone verification, account deletion, recovery, and general session administration UI remain deferred.

### Product catalogue, Recipe publication, and Dish catalogue

- active shared Products can be created and edited without changing IDs or Recipe relationships;
- Product and Recipe CSV preview/apply use the central alcohol policy and atomic writes;
- Recipe CLUB/PERSONAL ownership, owner-aware visibility, submission/rejection/publication, and row-locked moderation;
- publication and Dish synchronization occur in one SQLAlchemy transaction;
- existing attachments are not duplicated and active exact-name Dishes receive ordered variants without changing default or roles;
- otherwise publication creates one role-less Dish with the Recipe as default and only variant;
- no role, meal type, or repeatability value is inferred from Recipe content;
- exact selected Recipe persists on every meal assignment;
- shopping, equipment, and exports use assignment Recipe snapshots;
- central alcohol policy and archive markers preserve historical data while preventing prohibited active use;
- current Alembic head is `h10022`; immutable release tag `v0.1.0` remains at released head `h10021`.

### Actor-aware audit

- append-only AuditEvent persistence through `h10020`;
- actor snapshots and bounded recursive secret removal;
- semantic operational coverage through TH-0103;
- `account_profile_updated` shares the profile transaction, uses optimistic versions, suppresses no-op writes, and stores changed field names rather than contact values;
- `account_password_changed` shares the password/session transaction and stores versions, whether the current login was preserved, and the number of other logins revoked;
- phone numbers, social URLs, passwords, password hashes, cookies, raw session values, session hashes, tokens, exception details, and arbitrary request bodies are never account audit payloads;
- Administrator Audit UI exposes Russian labels for personal profile and password actions.

### Projects, preparation, documents, and operations

- Project catalogue, participant count, dates, meal boundaries, generation mode, persisted MealPlan/MealSlotDish, shopping, checklist, equipment, readiness, and recalculation;
- compact Project Overview and routed Menu, Shopping, Equipment, and Documents work areas;
- temporary global navigation drawer below desktop width;
- complete Russian Project PDF/workbook, compatibility files, and coordinated ZIP;
- one immutable club/document settings snapshot per package request;
- installation, update, backup, restore, health, LAN, recovery, and production-like Docker acceptance.

### Product acceptance and release readiness

- versioned first-release Product Acceptance and Release Readiness manifests remain tied to immutable `v0.1.0` and `h10021`;
- current Quality and Docker gates migrate and validate post-release head `h10022`;
- Final Release Readiness verifies the released migration cycle by checking out immutable tag `v0.1.0`;
- TH-0104 critical Backend and Chrome scenarios cover profiles, contacts, vCard, password changes, account navigation, mobile layout, and logout;
- exact-head workflows, PostgreSQL backup/restore, and immutable tag verification remain required;
- no active release-blocking debt.

## 5. Current active work

- TH-0061.5 — operational maintenance of the completed menu rules engine.

TH-0104 is complete after exact-head verification. No later post-release capability is selected automatically.

## 6. Immediate sequence

1. Operate the local stack using `docs/DEPLOYMENT_CHECKLIST.md`.
2. Use `/account` to maintain personal contact details and access active club contacts.
3. Use the Administrator Audit surface to review covered operational and account events.
4. Select later product work only through another explicit Product Owner decision.

## 7. Development rules

- Do not invent missing business requirements.
- Do not add microservices or multi-tenant infrastructure.
- Do not put business rules or permission decisions only in React.
- Do not expose account contact data outside authenticated active-user boundaries.
- Do not record account contact values, passwords, hashes, cookies, or session tokens in audit payloads.
- Do not infer Dish generator roles from Recipe content without a separate approved design.
- Do not implement ORM-wide automatic auditing; record semantic actions in owning transactions.
- Do not describe a feature as implemented unless code and tests confirm it.
- Architecture or stack changes require Product Owner approval and an ADR.
- One logical task is squash-merged to `main`.
- The released `v0.1.0` tag and its migration contract remain immutable.
- Documentation, task state, roadmap, and technical debt are updated with code.
