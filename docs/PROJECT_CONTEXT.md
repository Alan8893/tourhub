# TourHub — PROJECT_CONTEXT

Version: 0.1.0

Last update: 2026-07-20

Status: Post-release System Settings and mail audit coverage delivered — TH-0101

## 1. Product boundary

TourHub is a local ERP application for one tourist club.

- One installation represents one club.
- Multi-tenant support is prohibited.
- The runtime supports multiple invited users inside the same club.
- Registration is invitation-only after one-time Administrator bootstrap.
- Approved roles are Administrator, Instructor, and Verified Instructor.
- Participant profiles are outside the released workflow; calculations use participant count.
- Alcohol is prohibited without exceptions through one Backend policy.
- Paid or externally hosted runtime services are not used.

The approved target scope is defined in `PRODUCT_SPEC.md`. The current state is defined by code, tests, Product Acceptance/Release Readiness evidence, `PROJECT_STATUS.md`, `ARCHITECTURE_CURRENT.md`, and `DOMAIN_CURRENT.md`.

## 2. Released product workflow

```text
Administrator bootstrap and invitations
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

The complete first-release sequence is delivered through TH-0093 and tagged `v0.1.0`. TH-0095 improves Project workspace navigation, TH-0097 adds shared Product editing, TH-0098 closes the publication-to-Dish workflow, TH-0099 adds Project audit coverage, TH-0100 adds transactional audit coverage for menu generation/regeneration and manual MealSlot changes, and TH-0101 adds System Settings and Administrator mail-operation audit coverage.

## 3. Architecture

TourHub remains a modular monolith.

### Frontend

- React;
- TypeScript;
- Vite;
- Material UI;
- TanStack Query;
- React Router.

Frontend owns presentation, responsive navigation, Project workspace routing, Product create/edit state, Dish generator-readiness presentation, query invalidation, safe AuditEvent rendering/filtering, and download controls. It does not own business validation, generation rules, Recipe publication synchronization, role inference, calculations, authorization, unit conversion, or audit sanitization.

### Backend

- Python 3.13;
- FastAPI;
- SQLAlchemy 2.x;
- Alembic;
- Pydantic v2;
- PostgreSQL 18 in the release runtime;
- Redis configuration;
- deterministic calculation, document, audit, and catalogue-policy boundaries.

Backend owns validation, persistence, identity/authorization, Product policy, Recipe ownership/lifecycle, published Recipe-to-Dish synchronization, Dish variant selection, menu generation, manual MealSlot mutation, catalogue import, central alcohol policy, recalculation, mail boundaries, document generation, and semantic audit rules in owning transactions.

### Runtime

Development starts with:

```bash
docker compose up -d --build
```

The operator path uses `docker-compose.release.yml`. Frontend, Backend, PostgreSQL, and Redis run locally. PostgreSQL and Redis remain internal to the release network. Redis is available but no released business workflow depends on it.

## 4. Released baseline

### Access and users

- one-time Administrator bootstrap and invitation-only registration;
- password hashing and server-owned HttpOnly sessions;
- working SMTP invitation delivery with manual fallback;
- roles, activation controls, optimistic user versions, and last-active-Administrator protection;
- preparation access for all approved active roles;
- Administrator-only settings, invitations, users, mail operations, and audit reads;
- multiple sessions, current-role resolution, deactivation revocation, protected-401 handling, exact route return, and visible role.

### Product catalogue, Recipe publication, and Dish catalogue

- active shared Products can be created and edited without changing IDs or Recipe relationships;
- Recipe CLUB/PERSONAL ownership, owner-aware visibility, submission/rejection/publication, and row-locked moderation;
- publication and Dish synchronization occur in one SQLAlchemy transaction;
- existing attachments are not duplicated and active exact-name Dishes receive ordered variants without changing default or roles;
- otherwise publication creates one role-less Dish with the Recipe as default and only variant;
- role-less Dishes display `Не настроено для генератора`; configured Dishes display `Готово для генератора`;
- no role, meal type, or repeatability value is inferred from Recipe content;
- exact selected Recipe persists on every meal assignment;
- shopping, equipment, and exports use assignment Recipe snapshots;
- central alcohol policy and archive markers preserve historical data while preventing prohibited active use;
- `h10021` remains the single Alembic head.

### Actor-aware audit

- append-only AuditEvent persistence through `h10020`;
- actor snapshots and bounded recursive secret removal;
- semantic user-access and Recipe moderation events in owning transactions;
- Project creation, participant recalculation, generation-mode updates, and full preparation orchestration events through TH-0099;
- menu generation/regeneration and manual MealSlot add/remove/replace events through TH-0100;
- all six typed System Settings owners record semantic before/after diffs with real Administrator attribution and no-op suppression through TH-0101;
- settings mutation, focused settings history, and AuditEvent share the existing settings service commit/rollback boundary;
- Club image changes record only configured state, MIME type, and byte size;
- SMTP connection checks and fixed test-message operations record safe result status, attempts, optional recipient, and bounded non-secret context;
- SMTP passwords, deployment environment values, protocol transcripts, exception details, invitation/session values, tokens, and arbitrary request bodies are never audit payloads;
- Administrator-only Audit UI/API expose Russian User, Recipe, Project, Menu, MealSlot, System Settings, and Mail labels and filters.

### Projects, preparation, documents, and operations

- Project catalogue, participant count, dates, meal boundaries, generation mode, persisted MealPlan/MealSlotDish, shopping, checklist, equipment, readiness, and recalculation;
- compact Project Overview and routed Menu, Shopping, Equipment, and Documents work areas;
- temporary global navigation drawer below desktop width;
- complete Russian Project PDF/workbook, compatibility files, and coordinated ZIP;
- one immutable club/document settings snapshot per package request;
- installation, update, backup, restore, health, LAN, recovery, and production-like Docker acceptance.

### Product acceptance and release readiness

- versioned Product Acceptance and Release Readiness manifests;
- critical Backend and Chrome gates, including published Recipe Dish synchronization and Project/Menu/MealSlot/System Settings/Mail audit coverage;
- Alembic accepted head fixed at `h10021`;
- real PostgreSQL 18 migration-cycle verification;
- exact-head push workflows for required gates;
- immutable lightweight tag `v0.1.0` at the recorded release SHA;
- backup-based production rollback boundary;
- no active release-blocking debt.

## 5. Current active work

- TH-0061.5 — operational maintenance of the completed menu rules engine.

TH-0101 is complete. Invitation lifecycle/delivery results, catalogue/import, shopping, equipment, and document-generation audit domains remain deferred until another explicit Product Owner decision.

## 6. Immediate sequence

1. Operate the released local stack using `docs/DEPLOYMENT_CHECKLIST.md`.
2. Use the Administrator Audit surface to review user, Recipe, Project, Menu, MealSlot, System Settings, and Mail events.
3. Select any later audit or product slice only through another explicit Product Owner decision.

## 7. Development rules

- Do not invent missing business requirements.
- Do not add microservices or multi-tenant infrastructure.
- Do not put business rules or permission decisions only in React.
- Do not infer Dish generator roles from Recipe content without a separate approved design.
- Do not implement ORM-wide automatic auditing; record semantic actions in owning transactions.
- Do not describe a feature as implemented unless code and tests confirm it.
- Architecture or stack changes require Product Owner approval and an ADR.
- One logical task is squash-merged to `main`.
- Released v0.1.0 scope may change only through an explicit post-release task.
- Documentation, task state, roadmap, and technical debt are updated with code.
