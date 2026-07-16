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

### Menu foundation and editor

- persisted MealPlan, MealPlanDay, MealSlot, and MealSlotDish;
- first/last meal schedule and one-day handling;
- domain order `breakfast`, `snack`, `lunch`, `dinner`;
- multiple dishes per MealSlot;
- backend add, replace, and remove operations;
- correct MealSlotDish relation identifiers in API and frontend mutations;
- compact Russian editor, explicit actions, confirmations, loading/error/success states;
- responsive desktop, tablet, and mobile layouts;
- transactional purchasing recalculation after MealSlot changes.

### TH-0061.5 delivered menu rules

Merged through PR #59, #60, #61, #64, #65, #66, and #67:

- persisted roles `main`, `addition`, `drink`, and `snack`;
- compatibility per `(dish, role, meal_type)`;
- no inference from names, recipes, ingredients, history, or manual placement;
- readiness minimums for breakfast, snack, lunch, and dinner;
- role-aware project meal-plan generation;
- required `main` for breakfast/lunch/dinner and required `snack` for snack;
- optional compatible `addition` and `drink`;
- stable `main → addition → drink` order;
- same-day uniqueness and repeatability per role assignment;
- trip-calendar-day three-day diversity for non-repeatable `main` dishes;
- day-four reuse and repeatable-main bypass;
- exclusion of archived-recipe and unclassified dishes from automatic generation;
- explicit warnings instead of hidden incompatible fallback;
- persisted manual-slot marker through Alembic revision `h10002`;
- authoritative preservation of non-empty and empty manual slots during regeneration;
- reuse of one MealPlan per project;
- API, engine, service, persistence, migration, and real ORM integration coverage.

Quality #271 passed before PR #66 merge and Quality #273 passed before PR #67 merge.

### Shopping and documents

- ingredient aggregation;
- package-rounding foundation;
- purchase list and checklist;
- transactional refresh and checklist-state preservation;
- PDF/Excel/package export foundations.

## IN PROGRESS

### TH-0061 — Guided project preparation

- complete the guided Russian preparation workflow;
- connect menu, purchasing, packaging, equipment, and export steps;
- verify the complete single-club preparation journey.

### TH-0061.5 — Generation warning lifecycle

Draft PR #69 implements the final currently approved rules-engine slice:

- Alembic revision `h10003` adds an ordered warning snapshot to MealPlan;
- POST generation persists the warnings from that exact generation;
- subsequent GET responses return the persisted snapshot;
- catalogue changes do not rewrite historical warnings without regeneration;
- regeneration replaces the snapshot atomically, including clearing it to `[]`;
- public API regression coverage verifies the complete lifecycle.

Remaining operational work after PR #69:

1. maintain and complete explicit classification of the active deployment catalogue;
2. define larger candidate thresholds or preference modes only after approved requirements.

## NEXT

### Shopping and equipment

- complete required/purchased/remainder presentation;
- optional responsible-person text;
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
