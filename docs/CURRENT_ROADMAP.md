# TourHub Current Roadmap

Status date: 2026-07-15

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
- PostgreSQL 18;
- Redis runtime service and configuration;
- Alembic migrations with one-head CI validation;
- backend tests;
- selected Ruff and strict mypy gates;
- frontend tests, dependency audit, production build, and browser acceptance;
- PostgreSQL backup/restore scripts and CI smoke test.

### Projects

- project creation;
- project catalogue and workspace routing;
- participant count and duration;
- first and last meal persistence;
- backend meal-boundary validation;
- participant-count purchasing recalculation;
- LAN-safe same-origin frontend API routing.

### Recipes, products, and dishes

- recipe list/detail/create/rename;
- RecipeComponent CRUD and practical quantity modes;
- recipe note CRUD and ordering;
- archive, restore, and guarded delete;
- product list and creation;
- transactional CSV preview/apply;
- dish catalogue, create, rename, and active-recipe assignment;
- archived-recipe historical visibility;
- purchasing recalculation after Dish recipe replacement.

### Menu foundation

- persisted MealPlan, MealPlanDay, MealSlot, and MealSlotDish;
- first/last meal schedule;
- one-day range handling;
- domain order `breakfast`, `snack`, `lunch`, `dinner`;
- multiple dishes per MealSlot;
- backend add, replace, and remove operations;
- correct MealSlotDish identifiers in API and frontend mutations;
- deterministic same-day uniqueness;
- deterministic insufficient-catalogue fallback and immediate warning generation;
- archived-recipe assignment guard;
- purchasing recalculation after MealSlot changes;
- removal of unsupported meal-plan placeholders and invalid pseudo three-day cooldown.

### TH-0065 — Meal Plan Editor UX

Completed across PR #55 and PR #57:

- compact Russian dish rows;
- explicit replace, add, and confirmed remove flows;
- mutation loading, success, and error feedback;
- collapsible day sections with dish counts;
- full-width editor workspace;
- browser-level React/API acceptance for mutations and errors;
- no-overflow checks and screenshots at desktop, tablet, and 360 px mobile widths.

Quality run #169 passed before squash merge of PR #57. Product Owner visual acceptance was recorded and the task is closed.

### Shopping and documents

- ingredient aggregation;
- package rounding foundation;
- purchase list and checklist;
- transactional refresh and checklist-state preservation;
- PDF/Excel/package export foundations.

### TH-0070 — Critical meal-plan stabilization

Completed by PR #54. Quality passed for backend tests, selected Ruff and strict mypy, Alembic, frontend tests/build/audit, and PostgreSQL backup/restore.

## IN PROGRESS

### TH-0061 — Guided project preparation

- complete guided Russian preparation workflow;
- connect the corrected editor, purchasing, and export steps;
- verify the complete single-club preparation journey.

### TH-0061.5 — Meal Composition Rules Engine

ADR-013 now approves a two-dimensional persisted classification:

- normalized `dish_meal_roles` owned by Dish;
- roles `main`, `addition`, `drink`, and `snack`;
- normalized `dish_meal_role_meal_types` owned by each role assignment;
- meal types `breakfast`, `snack`, `lunch`, and `dinner`;
- multiple roles per Dish;
- repeatability per `(dish, role)`;
- compatibility per `(dish, role, meal_type)`;
- no inference from names, recipes, ingredients, or historical placement.

Backend persistence/API slice on PR #59:

- `DishMealRoleORM` and `DishMealRoleMealTypeORM`;
- Alembic revision `h10001` with both normalized tables;
- role and meal-type database constraints with cascading foreign keys;
- Dish list/detail response contracts;
- atomic full classification replacement endpoint;
- clearing, duplicate, empty, invalid, incompatible, and missing-dish coverage;
- unchanged current generation behavior.

Frontend editor slice on PR #60:

- Russian role and meal-type controls in the Dish catalogue;
- multiple roles and per-role repeatability;
- explicit compatible meal types for every selected role;
- local validation before API mutation;
- visible role/meal-type classification in list and detail views;
- exact Axios/React Query API acceptance;
- backend error rendering and responsive 1280/768/360 px screenshots.

Quality run #197 is successful for PR #59. Quality run #206 is successful for the stacked PR #60.

## NEXT

### Catalogue classification and readiness

1. Merge PR #59.
2. Retarget PR #60 to `main`, rerun Quality, and merge it.
3. Classify the active catalogue explicitly by role and meal type.
4. Define minimum readiness thresholds per generated meal type.
5. Return visible Russian warnings for missing `main`, `snack`, or optional supporting pools.
6. Keep unclassified dishes manually selectable and excluded from automatic role selection.

### Role-aware composition

1. Filter candidates by both persisted role and current meal type.
2. Implement breakfast, snack, lunch, and dinner composition.
3. Implement calendar-day three-day diversity for main dishes.
4. Allow explicitly repeatable drinks and additions.
5. Preserve manual selections as authoritative.
6. Exclude archived-recipe dishes from automatic selection.
7. Persist or reconstruct warnings for later reads.
8. Add unit, service, API, frontend, and recalculation coverage.

### Shopping and equipment

- complete required/purchased/remainder presentation;
- optional responsible-person text;
- recipe equipment requirements;
- maximum simultaneous equipment aggregation;
- manual equipment overrides;
- equipment recalculation after participant and menu changes.

### Documents and acceptance

- final Russian PDF;
- final Russian Excel workbook;
- club name and logo settings;
- installation/update documentation;
- Docker image/build CI gate;
- desktop and mobile acceptance.

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
