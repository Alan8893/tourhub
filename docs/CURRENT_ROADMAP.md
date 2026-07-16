# TourHub Current Roadmap

Status date: 2026-07-16

## Product goal

Deliver a stable local MVP for one tourist club without changing the approved architecture.

```text
Project
  → Menu
  → Recipes and dishes
  → Shopping and packaging
  → Equipment
  → Russian PDF and Excel
```

## DONE

### Infrastructure

- Dockerfiles and Docker Compose;
- PostgreSQL 18 and Redis runtime configuration;
- Alembic migrations with one-head CI validation;
- backend tests, selected Ruff, and strict mypy gates;
- frontend tests, dependency audit, production build, and browser acceptance;
- PostgreSQL backup/restore scripts and CI smoke test;
- LAN-safe same-origin frontend API routing;
- responsive temporary mobile drawer with permanent desktop sidebar.

### Projects

- project creation and catalogue;
- project workspace routing;
- participant count and duration;
- first and last meal persistence;
- backend meal-boundary validation;
- participant-count purchasing recalculation.

### Recipes, products, and dishes

- recipe list/detail/create/rename;
- RecipeComponent CRUD and practical quantity modes;
- recipe notes and ordering;
- archive, restore, and guarded delete;
- product list and creation;
- transactional CSV preview/apply;
- dish catalogue, create, rename, and active-recipe assignment;
- archived-recipe historical visibility;
- purchasing recalculation after Dish recipe replacement;
- normalized Dish roles and role-specific meal-type compatibility;
- per-role repeatability;
- atomic classification replacement API;
- Russian role/meal-type editor;
- deterministic catalogue-readiness API and warnings.

### Menu and TH-0061.5 rules

Merged through PR #59, #60, #61, #64, #65, #66, #67, and #69:

- persisted MealPlan, MealPlanDay, MealSlot, and MealSlotDish;
- first/last meal scheduling and multiple dishes per slot;
- compact responsive Russian editor;
- persisted roles `main`, `addition`, `drink`, and `snack`;
- compatibility per `(dish, role, meal_type)`;
- no inference from names, recipes, ingredients, history, or manual placement;
- role-aware generation with required and optional composition roles;
- stable `main → addition → drink` order;
- same-day uniqueness and repeatability per role assignment;
- trip-calendar-day three-day diversity for non-repeatable `main` dishes;
- day-four reuse and repeatable-main bypass;
- exclusion of archived-recipe and unclassified dishes from automatic generation;
- explicit warnings instead of hidden incompatible fallback;
- persisted manual-slot marker through Alembic revision `h10002`;
- authoritative preservation of non-empty and empty manual slots during regeneration;
- reuse of one MealPlan per project;
- ordered generation-warning snapshot through Alembic revision `h10003`;
- identical warnings on generation and later reads;
- atomic warning replacement and clearing on regeneration;
- transactional purchasing recalculation after MealSlot changes.

Quality #271 passed before PR #66 merge, Quality #273 before PR #67 merge, and Quality #280 before PR #69 merge.

### Shopping and documents foundation

- ingredient aggregation;
- package-rounding foundation;
- purchase list and purchase checklist persistence;
- purchased quantity and checked-state persistence;
- transactional refresh and checklist-state preservation;
- PDF/Excel/package export foundations.

## IN PROGRESS

### TH-0061 — Guided project preparation

Draft PR #70 implements the first shopping-review slice:

- product names in checklist responses;
- required, purchased, and remaining quantity presentation;
- non-negative remaining calculation and purchased-quantity validation;
- editable Russian purchase checklist in the project workspace;
- completion progress and explicit loading/error/success states;
- responsive controls and 360 px no-overflow browser acceptance;
- backend API and frontend state regression coverage.

The slice intentionally keeps shopping aggregation and package-rounding calculations unchanged.

## NEXT

### Shopping and packaging

- complete package-count and package-surplus review presentation;
- add optional responsible-person text;
- connect shopping review to the complete guided preparation sequence.

### Equipment

- persist recipe equipment requirements;
- aggregate maximum simultaneous equipment need;
- support manual equipment overrides;
- recalculate equipment after participant and menu changes.

### Documents and acceptance

- final Russian PDF;
- final Russian Excel workbook;
- club name and logo settings;
- installation/update documentation;
- Docker image/build CI gate;
- full desktop and mobile release acceptance.

## LATER

- invitation-only registration;
- Administrator, Instructor, and Verified Instructor roles;
- backend permission enforcement;
- recipe ownership and multiple variants;
- publication and moderation;
- audit log;
- participant profiles;
- routes and GPX;
- logistics and load distribution;
- warehouse balances;
- price aggregation.

Multi-tenant support and microservices remain prohibited.
