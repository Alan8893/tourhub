# TourHub — PROJECT_CONTEXT

Version: 0.1.0

Last update: 2026-07-19

Status: Post-release Product catalogue editing delivered — TH-0097

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

The approved target scope is defined in `PRODUCT_SPEC.md`. The released first-release state is defined by code, tests, `PRODUCT_ACCEPTANCE.md`, `product_acceptance_manifest.json`, `release_readiness_manifest.json`, `PROJECT_STATUS.md`, `ARCHITECTURE_CURRENT.md`, and `DOMAIN_CURRENT.md`.

## 2. Released product workflow

The approved Russian local workflow is accepted, feature frozen, and release-ready:

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
  → Final migration and release readiness
```

The complete first-release sequence is delivered through TH-0093 and tagged `v0.1.0`. TH-0095 improves Project workspace navigation and responsive presentation. TH-0097 adds shared Product catalogue editing while preserving RecipeComponent calculation inputs and the released database boundary.

## 3. Architecture

TourHub remains a modular monolith.

### Frontend

- React;
- TypeScript;
- Vite;
- Material UI;
- TanStack Query;
- React Router.

Frontend owns presentation, responsive application navigation, Project workspace routing, Product create/edit form state, API integration, server-projected capabilities, safe audit responses, and download controls. It does not own business validation, alcohol classification, document content, generation, lifecycle, calculation, authorization, unit conversion, or audit sanitization.

### Backend

- Python 3.13;
- FastAPI;
- SQLAlchemy 2.x;
- Alembic;
- Pydantic v2;
- PostgreSQL 18 in the release runtime;
- Redis configuration;
- deterministic calculation, document, audit, and catalogue-policy boundaries.

Backend owns validation, persistence, identity/authorization, Product catalogue policy, Recipe ownership/lifecycle, Dish variant selection, menu generation, catalogue import, central alcohol policy, recalculation, mail boundaries, document content/generation, and audit recording/query rules.

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

### Product catalogue, Recipe ownership, publication, Dish variants, and alcohol policy

- active shared Products can be created and edited from the Recipe component workflow;
- Product edits preserve identifiers and existing Recipe relationships;
- Product name, category, catalogue unit, and package size remain Backend-validated;
- changing a Product catalogue unit never converts or rewrites RecipeComponent amount/unit values;
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

- project catalogue, participant count, duration, dates, meal boundaries, Recipe generation mode, persisted MealPlan/MealSlotDish, shopping, checklist, equipment, readiness, and recalculation;
- compact Project Overview at `/projects/:id`;
- routed Menu, Shopping, Equipment, and Documents work areas under `/projects/:id/*`;
- Project settings dialog for Recipe generation mode;
- separate Shopping calculation/packing and checklist views;
- temporary global navigation drawer below desktop width and a permanent sidebar on desktop;
- readable stacked checklist controls through tablet widths;
- complete Russian Project PDF and workbook sheets `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование`;
- compatibility purchase/equipment PDF/XLSX/print and coordinated ZIP;
- compact full-package download on Overview and complete download controls in Documents;
- one immutable club/document settings snapshot per package request;
- installation, update, backup, restore, health, LAN, recovery, and production-like Docker acceptance.

### Product acceptance and release readiness

- versioned Product Acceptance and Release Readiness manifests;
- dedicated selected Backend and six-scenario Chrome Product Acceptance gate;
- Alembic accepted head fixed at `h10021`;
- real PostgreSQL 18 `h10020 → h10021 → h10020 → h10021` verification with representative historical data;
- versioned deployment checklist and v0.1.0 release notes;
- exact-head push workflows for all required gates;
- lightweight `v0.1.0` tag on the verified merged SHA;
- backup-based production rollback boundary;
- no active release-blocking capability or operational debt.

## 5. Current active work

- TH-0061.5 — operational maintenance of the completed menu rules engine.

TH-0097 is complete. TH-0098 Published Recipe Dish Synchronization is the next Product Owner-approved post-release task and starts only from the merged TH-0097 baseline.

## 6. Immediate sequence

1. Operate the released local stack using `docs/DEPLOYMENT_CHECKLIST.md`.
2. Use Product catalogue editing to correct shared Product name, category, unit, or package size without recreating Recipe components.
3. Deliver TH-0098 as a separate task: synchronize a published Recipe into Dishes without inferring generator roles.

## 7. Development rules

- Do not invent missing business requirements.
- Do not add microservices or multi-tenant infrastructure.
- Do not put business rules or permission decisions only in React.
- Do not describe a feature as implemented unless code and tests confirm it.
- Architecture or stack changes require Product Owner approval and an ADR.
- One logical task is squash-merged to `main`.
- Released v0.1.0 scope may change only through an explicit post-release task; fixes require regression, security, operational, or approved UX evidence.
- Documentation, task state, roadmap, and technical debt are updated with code.
