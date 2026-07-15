# TourHub — PROJECT_CONTEXT

Version: 0.0.2-alpha

Last update: 2026-07-15

Status: Active Development

## 1. Product boundary

TourHub is a local ERP application for one tourist club.

- One installation represents one club.
- Multi-tenant support is prohibited.
- The current delivery phase is single-user.
- Invitation-only access and user roles are deferred until the single-user preparation workflow is complete.
- Participant profiles are not part of the current MVP workflow; calculations use participant count.
- Paid external services are not used.

The approved target product scope is defined in `PRODUCT_SPEC.md`. The implemented state is defined by repository code, tests, `PROJECT_STATUS.md`, `ARCHITECTURE_CURRENT.md`, and `DOMAIN_CURRENT.md`.

## 2. Current product goal

Complete and stabilize the Russian local workflow:

```text
Project
  → Menu
  → Recipes and dishes
  → Shopping and packaging
  → Equipment
  → PDF and Excel
```

The critical contract stabilization from TH-0070 is complete. Current work prioritizes a usable and tested Meal Plan Editor before new menu-intelligence metadata and rules.

## 3. Architecture

TourHub remains a modular monolith.

### Frontend

- React;
- TypeScript;
- Vite;
- Material UI;
- TanStack Query;
- React Router.

Frontend owns presentation, form state, navigation, and API integration. It does not own business validation, menu generation, shopping calculations, or authorization decisions.

### Backend

- Python 3.13;
- FastAPI;
- SQLAlchemy 2.x;
- Alembic;
- Pydantic v2;
- PostgreSQL;
- Redis configuration;
- deterministic calculation engines.

Backend owns business validation, persistence, generation, catalogue import, recalculation, and document generation.

### Runtime

The local stack starts with:

```bash
docker compose up --build
```

Docker Compose includes frontend, backend, PostgreSQL, and Redis. Redis is available in the runtime stack but no business workflow currently depends on it.

## 4. Implemented baseline

### Projects

- creation;
- catalogue at `/projects`;
- workspace at `/projects/{id}`;
- participant count and trip duration;
- first and last meal context;
- backend validation of meal boundaries;
- participant-count purchasing recalculation.

### Recipes and products

- recipe library and detail;
- recipe create and rename;
- components and practical quantity modes;
- notes and priority ordering;
- archive, restore, and guarded deletion;
- product list and creation;
- transactional CSV preview and apply.

### Dishes

- dish catalogue;
- create and rename;
- one selected active recipe per Dish;
- archived-recipe history;
- prevention of new archived-recipe assignment;
- purchasing recalculation after recipe replacement.

### Menu

- persisted MealPlan, MealPlanDay, MealSlot, and MealSlotDish;
- first/last meal schedule;
- breakfast, snack, lunch, dinner order;
- one-day schedule handling;
- multiple dishes per MealSlot;
- add, replace, and remove operations;
- real MealSlotDish identifiers in the API;
- deterministic same-day uniqueness while unused dishes remain;
- insufficient-catalogue warning and deterministic fallback.

Meal-role composition and calendar-day three-day diversity are not implemented. No persisted MealDishRole exists.

### Shopping and documents

- ingredient aggregation;
- package rounding foundation;
- purchase list and checklist;
- transactional recalculation after participant, MealSlot, and Dish recipe changes;
- preservation of checklist state where products remain;
- PDF and Excel purchase export foundations;
- PostgreSQL backup and restore scripts.

## 5. Current active work

- TH-0061 — guided project preparation workflow;
- TH-0061.5 — Meal Composition Rules Engine;
- TH-0065 — Meal Plan Editor UX.

TH-0070 was completed by PR #54 with a successful Quality workflow. New composition work must still wait for approved persisted meal-role metadata.

## 6. Immediate sequence

1. Complete Meal Plan Editor UX on the corrected API contract.
2. Add React/API integration coverage for the editor.
3. Define approved persisted meal-role metadata.
4. Implement role-aware composition and calendar-day diversity.
5. Complete packaging presentation and equipment.
6. Complete Russian exports and local MVP acceptance.
7. Introduce invitation-only access, roles, ownership, moderation, and audit logging.

## 7. Development rules

- Do not invent missing business requirements.
- Do not add microservices or multi-tenant infrastructure.
- Do not put business rules only in React.
- Do not describe a feature as implemented unless repository code and tests confirm it.
- Architecture or stack changes require Product Owner approval and an ADR.
- One logical task is squash-merged to `main`.
- Documentation, task state, roadmap, and technical debt are updated with code.
