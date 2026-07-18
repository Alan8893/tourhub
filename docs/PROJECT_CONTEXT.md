# TourHub — PROJECT_CONTEXT

Version: 0.0.4-alpha

Last update: 2026-07-18

Status: Active Development

## 1. Product boundary

TourHub is a local ERP application for one tourist club.

- One installation represents one club.
- Multi-tenant support is prohibited.
- The runtime supports multiple invited users inside the same club.
- Registration is invitation-only after one-time Administrator bootstrap.
- Approved roles are Administrator, Instructor, and Verified Instructor.
- Participant profiles are not part of the current MVP workflow; calculations use participant count.
- Paid external services are not used.

The approved target product scope is defined in `PRODUCT_SPEC.md`. The implemented state is defined by repository code, tests, `PROJECT_STATUS.md`, `ARCHITECTURE_CURRENT.md`, and `DOMAIN_CURRENT.md`.

## 2. Current product goal

Complete and stabilize the Russian local workflow:

```text
Administrator bootstrap and invitations
  → Project
  → Menu
  → Club and personal recipes
  → Dishes
  → Shopping and packaging
  → Equipment
  → PDF, Excel, print, and ZIP
```

The complete guided preparation baseline, production-like runtime, typed System Settings, first-release Access foundation, working SMTP invitation delivery, multi-user operational readiness, and Recipe Ownership Foundation are complete through PR #96. The next product capability is recipe publication and moderation.

## 3. Architecture

TourHub remains a modular monolith.

### Frontend

- React;
- TypeScript;
- Vite;
- Material UI;
- TanStack Query;
- React Router.

Frontend owns presentation, form state, navigation, and API integration. It renders server-projected capabilities but does not own business validation, menu generation, shopping calculations, or authorization decisions.

### Backend

- Python 3.13;
- FastAPI;
- SQLAlchemy 2.x;
- Alembic;
- Pydantic v2;
- PostgreSQL 18 in the release runtime;
- Redis configuration;
- deterministic calculation engines.

Backend owns business validation, persistence, identity and authorization decisions, recipe ownership, menu generation, catalogue import, recalculation, mail delivery boundaries, and document generation.

### Runtime

The development stack starts with:

```bash
docker compose up -d --build
```

The operator release path uses `docker-compose.release.yml`. Frontend, Backend, PostgreSQL, and Redis run locally. PostgreSQL and Redis remain internal to the release Compose network. Redis is available but no current business workflow depends on it.

## 4. Implemented baseline

### Access and users

- one-time first-Administrator bootstrap;
- password hashing and server-owned HttpOnly sessions;
- Administrator-created one-time invitations and automatic SMTP delivery with manual-link fallback;
- invited-user creation, role and activity administration, optimistic versions, and final-active-Administrator protection;
- preparation access for active Administrator, Instructor, and Verified Instructor users;
- Administrator-only settings, invitation management, user administration, and mail operations;
- multiple independent sessions, current-role resolution, complete deactivation revocation, centralized 401 handling, exact route return, and visible current role.

### Recipe ownership

- Recipe scope is CLUB or PERSONAL;
- existing catalogue recipes are CLUB and have no owner;
- interactive new recipes are PERSONAL and owned by the current authenticated user;
- Administrator sees and manages all recipes;
- Verified Instructor edits CLUB and owned PERSONAL recipes;
- Instructor edits owned PERSONAL recipes and reads CLUB recipes;
- unrelated PERSONAL recipes are hidden;
- components, notes, and equipment requirements share the same Backend ownership boundary;
- permanent deletion remains Administrator-only and preserves Dish usage guards;
- frontend labels scope and owner and follows server-projected capabilities.

### Projects and preparation

- project catalogue and workspace;
- participant count, duration, start date, first and last meal;
- Backend validation of meal boundaries;
- persisted MealPlan, MealPlanDay, MealSlot, and MealSlotDish;
- automatic role-aware menu generation and manual editing;
- calendar-day diversity, authoritative manual slots, and persisted generation warnings;
- participant, menu, recipe, shopping, and equipment recalculation boundaries;
- reload-safe preparation readiness.

### Catalogue, shopping, equipment, documents, and operations

- products, recipe components/notes/equipment requirements, dishes, and CSV preview/apply;
- normalized Dish meal roles, compatibility, and repeatability;
- persisted purchase list, packaging quantities, checklist, comments, responsible-person text, equipment rows, overrides, and removals;
- typed club/site/document/module/invitation/mail settings;
- Russian purchase/equipment PDF, Excel, print, and coordinated ZIP outputs;
- immutable club/document settings snapshot per generation request;
- installation, update, backup, restore, health, LAN, recovery, and production-like Docker acceptance.

## 5. Current active work

- TH-0061.5 — operational maintenance of the completed menu rules engine.

The next task should implement recipe submission, review, publication, rejection, and resubmission from the ownership foundation now on `main`.

## 6. Immediate sequence

1. Implement recipe publication and moderation lifecycle.
2. Implement multiple Recipe variants per Dish and club/personal generation modes.
3. Enforce the central alcohol prohibition across Product, Recipe, and import paths.
4. Implement actor-aware audit history.
5. Complete consolidated Russian exports and product acceptance.
6. Freeze features, run the final migration cycle, and complete release gates.

## 7. Development rules

- Do not invent missing business requirements.
- Do not add microservices or multi-tenant infrastructure.
- Do not put business rules or permission decisions only in React.
- Do not describe a feature as implemented unless repository code and tests confirm it.
- Architecture or stack changes require Product Owner approval and an ADR.
- One logical task is squash-merged to `main`.
- Documentation, task state, roadmap, and technical debt are updated with code.
