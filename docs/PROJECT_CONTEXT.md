# TourHub — PROJECT_CONTEXT

Version: 0.0.8-alpha

Last update: 2026-07-19

Status: Feature Frozen — Final Migration and Release Readiness

## 1. Product boundary

TourHub is a local ERP application for one tourist club.

- One installation represents one club.
- Multi-tenant support is prohibited.
- The runtime supports multiple invited users inside the same club.
- Registration is invitation-only after one-time Administrator bootstrap.
- Approved roles are Administrator, Instructor, and Verified Instructor.
- Participant profiles are outside the current release workflow; calculations use participant count.
- Alcohol is prohibited without exceptions through one Backend policy.
- Paid external services are not used.

The approved target scope is defined in `PRODUCT_SPEC.md`. The accepted first-release state is defined by code, tests, `PRODUCT_ACCEPTANCE.md`, `product_acceptance_manifest.json`, `PROJECT_STATUS.md`, `ARCHITECTURE_CURRENT.md`, and `DOMAIN_CURRENT.md`.

## 2. Current product goal

The approved Russian local workflow is accepted and feature frozen:

```text
Administrator bootstrap and invitations
  → Project
  → Menu
  → Club and personal Recipes
  → Recipe publication and moderation
  → Dish Recipe variants and project generation modes
  → Shopping and packaging
  → Equipment
  → Complete PDF, Excel, compatibility files, and ZIP
  → Actor-aware operational accountability
  → Central alcohol prohibition
  → Product acceptance and feature freeze
```

The release-blocking functional sequence is complete through TH-0092 / PR #102. Final Migration and Release Readiness is the only next phase.

## 3. Architecture

TourHub remains a modular monolith.

### Frontend

- React;
- TypeScript;
- Vite;
- Material UI;
- TanStack Query;
- React Router.

Frontend owns presentation, form state, navigation, API integration, server-projected capabilities, safe audit responses, and download controls. It does not own business validation, alcohol classification, document content, generation, lifecycle, calculation, authorization, or audit sanitization.

### Backend

- Python 3.13;
- FastAPI;
- SQLAlchemy 2.x;
- Alembic;
- Pydantic v2;
- PostgreSQL 18 in the release runtime;
- Redis configuration;
- deterministic calculation, document, audit, and catalogue-policy boundaries.

Backend owns validation, persistence, identity/authorization, Recipe ownership/lifecycle, Dish variant selection, menu generation, catalogue import, central alcohol policy, recalculation, mail boundaries, document content/generation, and audit recording/query rules.

### Runtime

Development starts with:

```bash
docker compose up -d --build
```

The operator path uses `docker-compose.release.yml`. Frontend, Backend, PostgreSQL, and Redis run locally. PostgreSQL and Redis remain internal to the release network. Redis is available but no current business workflow depends on it.

## 4. Accepted first-release baseline

### Access and users

- one-time Administrator bootstrap and invitation-only registration;
- password hashing and server-owned HttpOnly sessions;
- working SMTP invitation delivery with manual fallback;
- roles, activation controls, optimistic user versions, and last-active-Administrator protection;
- preparation access for all approved active roles;
- Administrator-only settings, invitations, users, mail operations, and audit reads;
- multiple sessions, current-role resolution, deactivation revocation, protected-401 handling, exact route return, and visible role.

### Recipe ownership, publication, Dish variants, and alcohol policy

- Recipe CLUB/PERSONAL scope, owner-aware visibility, submission/rejection/publication, and row-locked moderation;
- ordered CLUB/current-actor PERSONAL Recipe variants per Dish;
- Project modes `club_only`, `club_and_personal`, and `personal_preferred`;
- exact selected Recipe persisted on every meal assignment;
- shopping, equipment, and exports use assignment Recipe snapshots;
- one complete-word normalized alcohol policy across Product, Recipe, Dish, lifecycle activation, and Product/Recipe CSV import;
- archive state and policy markers preserve historical records while excluding them from active catalogues/new selection;
- `h10021` archives existing prohibited Product → Recipe → default Dish records;
- policy-archived Recipes cannot be restored.

### Actor-aware audit

- append-only AuditEvent persistence through `h10020`;
- actor identity snapshots and bounded recursive secret removal;
- semantic user-access and Recipe moderation events in the same transaction;
- immutable moderation history and Administrator-only filtered UI/API.

### Projects, preparation, documents, and operations

- project catalogue/workspace, participant count, duration, dates, meal boundaries, Recipe generation mode, persisted MealPlan/MealSlotDish, shopping, checklist, equipment, readiness, and recalculation;
- complete Russian Project PDF and workbook sheets `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование`;
- compatibility purchase/equipment PDF/XLSX/print and coordinated ZIP;
- one immutable club/document settings snapshot per package request;
- installation, update, backup, restore, health, LAN, recovery, and production-like Docker acceptance.

### Product acceptance and freeze

- versioned machine-readable manifest for accepted capabilities, evidence, architecture boundaries, deferred scope, and acceptance commands;
- dedicated manifest, selected Backend, and six-scenario Chrome acceptance gate;
- Alembic head fixed at `h10021` for the accepted product baseline;
- no active release-blocking capability remains;
- optional gaps are explicitly deferred and non-blocking;
- first-release scope changes are restricted to acceptance defects, security fixes, final release-readiness work, and documentation corrections.

## 5. Current active work

- TH-0061.5 — operational maintenance of the completed menu rules engine.

No release-blocking feature task remains active. The next task starts Final Migration and Release Readiness without expanding the accepted first-release scope.

## 6. Immediate sequence

1. Run Final Migration and Release Readiness.
2. Create the release tag only after the final exact-head gates pass.

## 7. Development rules

- Do not invent missing business requirements.
- Do not add microservices or multi-tenant infrastructure.
- Do not put business rules or permission decisions only in React.
- Do not describe a feature as implemented unless code and tests confirm it.
- Architecture or stack changes require Product Owner approval and an ADR.
- One logical task is squash-merged to `main`.
- During feature freeze, only acceptance defect fixes, security fixes, final release-readiness work, and documentation corrections may change first-release scope.
- Documentation, task state, roadmap, and technical debt are updated with code.
