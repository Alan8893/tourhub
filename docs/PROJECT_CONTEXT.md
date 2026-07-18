# TourHub — PROJECT_CONTEXT

Version: 0.0.5-alpha

Last update: 2026-07-18

Status: Active Development

## 1. Product boundary

TourHub is a local ERP application for one tourist club.

- One installation represents one club.
- Multi-tenant support is prohibited.
- The runtime supports multiple invited users inside the same club.
- Registration is invitation-only after one-time Administrator bootstrap.
- Approved roles are Administrator, Instructor, and Verified Instructor.
- Participant profiles are outside the current MVP workflow; calculations use participant count.
- Paid external services are not used.

The approved target scope is defined in `PRODUCT_SPEC.md`. The implemented state is defined by code, tests, `PROJECT_STATUS.md`, `ARCHITECTURE_CURRENT.md`, and `DOMAIN_CURRENT.md`.

## 2. Current product goal

Complete and stabilize the Russian local workflow:

```text
Administrator bootstrap and invitations
  → Project
  → Menu
  → Club and personal Recipes
  → Recipe publication and moderation
  → Dish Recipe variants and project generation modes
  → Shopping and packaging
  → Equipment
  → PDF, Excel, print, and ZIP
```

The guided preparation baseline, production-like runtime, typed System Settings, Access/mail foundation, multi-user readiness, Recipe ownership, publication/moderation, and Dish Recipe variants with generation modes are complete through TH-0088 / PR #98. The next capability is the centralized alcohol prohibition.

## 3. Architecture

TourHub remains a modular monolith.

### Frontend

- React;
- TypeScript;
- Vite;
- Material UI;
- TanStack Query;
- React Router.

Frontend owns presentation, form state, navigation, and API integration. It renders server-projected capabilities and persisted selection results but does not own business validation, generation rules, lifecycle transitions, calculations, or authorization decisions.

### Backend

- Python 3.13;
- FastAPI;
- SQLAlchemy 2.x;
- Alembic;
- Pydantic v2;
- PostgreSQL 18 in the release runtime;
- Redis configuration;
- deterministic calculation engines.

Backend owns validation, persistence, identity and authorization, Recipe ownership/lifecycle, Dish variant selection, menu generation, catalogue import, recalculation, mail boundaries, and document generation.

### Runtime

Development starts with:

```bash
docker compose up -d --build
```

The operator path uses `docker-compose.release.yml`. Frontend, Backend, PostgreSQL, and Redis run locally. PostgreSQL and Redis remain internal to the release network. Redis is available but no current business workflow depends on it.

## 4. Implemented baseline

### Access and users

- one-time Administrator bootstrap and invitation-only registration;
- password hashing and server-owned HttpOnly sessions;
- automatic SMTP invitation delivery with manual fallback;
- roles, activation controls, optimistic user versions, and final-active-Administrator protection;
- preparation access for all approved active roles;
- Administrator-only settings, invitations, users, and mail operations;
- multiple sessions, current-role resolution, deactivation revocation, centralized protected-401 handling, exact route return, and visible role.

### Recipe ownership, publication, and Dish variants

- Recipe scope CLUB or PERSONAL;
- interactive owned PERSONAL drafts and shared published CLUB catalogue;
- owner submission, rejection feedback, editing, resubmission, and row-locked moderation;
- Administrator review of all submissions and Verified Instructor review of another user's submission;
- one published CLUB default plus an ordered set of CLUB/current-actor PERSONAL variants per Dish;
- Project modes `club_only`, `club_and_personal`, and `personal_preferred`;
- another user's PERSONAL Recipe remains private;
- exact selected Recipe persists on every meal assignment;
- manual assignments survive regeneration with their stored Recipe;
- shopping and equipment use assignment Recipe snapshots rather than mutable Dish defaults;
- responsive ownership, moderation, variant, mode, and selected-Recipe UI.

### Projects and preparation

- project catalogue/workspace, participant count, duration, dates, meal boundaries, and Recipe generation mode;
- persisted MealPlan, MealPlanDay, MealSlot, and MealSlotDish;
- role-aware menu generation, deterministic Recipe variant rotation, and manual editing;
- calendar-day diversity, authoritative manual slots, and persisted warnings;
- participant, menu, Recipe, shopping, and equipment recalculation boundaries;
- reload-safe preparation readiness.

### Catalogue, shopping, equipment, documents, and operations

- products, Recipe components/notes/equipment requirements, Dishes, and CSV preview/apply;
- normalized Dish roles, compatibility, and repeatability;
- persisted purchase list, packaging, checklist, comments, responsible person, equipment rows, overrides, and removals;
- typed club/site/document/module/invitation/mail settings;
- Russian purchase/equipment PDF, Excel, print, and coordinated ZIP;
- immutable club/document settings snapshot per generation request;
- installation, update, backup, restore, health, LAN, recovery, and production-like Docker acceptance.

## 5. Current active work

- TH-0061.5 — operational maintenance of the completed menu rules engine.

The next task should enforce the approved central alcohol prohibition without reopening completed Recipe or Access work.

## 6. Immediate sequence

1. Enforce the central alcohol prohibition across Product, Recipe, and import paths.
2. Implement actor-aware audit history, including immutable moderation history.
3. Complete consolidated Russian exports and product acceptance.
4. Freeze features, run the final migration cycle, and complete release gates.

## 7. Development rules

- Do not invent missing business requirements.
- Do not add microservices or multi-tenant infrastructure.
- Do not put business rules or permission decisions only in React.
- Do not describe a feature as implemented unless code and tests confirm it.
- Architecture or stack changes require Product Owner approval and an ADR.
- One logical task is squash-merged to `main`.
- Documentation, task state, roadmap, and technical debt are updated with code.
