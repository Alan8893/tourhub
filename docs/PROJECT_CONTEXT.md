# TourHub — PROJECT_CONTEXT

Version: 0.0.2-alpha

Last update: 2026-07-16

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

Critical meal-plan stabilization, Meal Plan Editor UX, persisted Dish classification, catalogue readiness, responsive mobile navigation, and the first role-aware generation slice are complete. Current work should extend this verified baseline rather than recreate it.

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

Backend owns business validation, persistence, menu generation, catalogue import, recalculation, and document generation.

### Runtime

The local stack starts with:

```bash
docker compose up -d --build
```

Docker Compose includes frontend, backend, PostgreSQL, and Redis. Redis is available in the runtime stack but no business workflow currently depends on it.

## 4. Implemented baseline

### Projects

- creation and catalogue at `/projects`;
- workspace at `/projects/{id}`;
- participant count and trip duration;
- first and last meal context;
- backend validation of meal boundaries;
- participant-count purchasing recalculation;
- LAN-safe same-origin API routing.

### Recipes and products

- recipe library and detail;
- recipe create and rename;
- components and practical quantity modes;
- notes and priority ordering;
- archive, restore, and guarded deletion;
- product list and creation;
- transactional CSV preview and apply.

### Dishes

- dish catalogue, create, and rename;
- one selected active recipe per Dish;
- archived-recipe history and assignment guards;
- purchasing recalculation after recipe replacement;
- normalized `dish_meal_roles`;
- normalized role-specific `dish_meal_role_meal_types`;
- roles `main`, `addition`, `drink`, and `snack`;
- repeatability per role assignment;
- atomic role/meal-type editing API;
- Russian responsive classification UI;
- structured catalogue-readiness API and warnings.

### Menu

- persisted MealPlan, MealPlanDay, MealSlot, and MealSlotDish;
- first/last meal schedule and one-day handling;
- breakfast, snack, lunch, dinner order;
- multiple dishes per MealSlot;
- add, replace, and remove operations;
- real MealSlotDish relation identifiers in the API;
- compact responsive Russian editor;
- role-aware automatic generation using both persisted role and meal type;
- `main` required for breakfast/lunch/dinner;
- `snack` required for snack;
- optional compatible `addition` and `drink`;
- stable `main → addition → drink` order;
- same-day uniqueness for non-repeatable assignments;
- repeatability per selected `(dish, role)`;
- unclassified and archived-recipe dishes excluded from automatic selection;
- explicit required-pool warnings instead of hidden incompatible fallback;
- generated compositions persisted through primary MealSlot rows and compatibility MealPlanItem rows.

MealPlanItem remains a legacy compatibility path. Calendar-day three-day main-dish diversity, regeneration that preserves manual choices, and warning reconstruction for later reads are not yet implemented.

### Shopping and documents

- ingredient aggregation;
- package-rounding foundation;
- purchase list and checklist;
- transactional recalculation after participant, MealSlot, and Dish recipe changes;
- preservation of checklist state where products remain;
- PDF and Excel purchase export foundations;
- PostgreSQL backup and restore scripts.

## 5. Current active work

- TH-0061 — guided project preparation workflow;
- TH-0061.5 — remaining menu diversity, regeneration, and warning-lifecycle rules.

TH-0065 and TH-0070 are complete. PR #59, #60, #61, #62, and #64 are merged. Quality run #254 passed on the exact PR #64 head, and the Product Owner verified the deployed behavior locally.

## 6. Immediate sequence

1. Maintain and complete explicit classification of the active deployment catalogue.
2. Implement calendar-day three-day diversity for main dishes.
3. Preserve manual selections during regeneration.
4. Persist or deterministically reconstruct generation warnings for later GET responses.
5. Complete guided preparation, packaging presentation, and equipment.
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
