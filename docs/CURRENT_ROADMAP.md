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
- persisted Dish roles and per-role meal-type compatibility;
- Russian role/meal compatibility editor;
- deterministic catalogue-readiness reporting and warnings;
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
- removal of unsupported meal-plan placeholders and invalid pseudo three-day cooldown;
- required-role automatic candidate filtering by persisted role and meal type;
- `main` selection for breakfast/lunch/dinner and `snack` selection for snack;
- unclassified and archived-recipe Dish exclusion from automatic generation;
- empty persisted MealSlots and explicit warnings when a required pool is missing;
- per-role repeatability during same-day selection.

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

### Mobile navigation

Completed by PR #62:

- closed-by-default temporary drawer on phones;
- permanent sidebar retained for tablet/desktop;
- mobile menu button and automatic close after navigation;
- full-width phone content and real-Chrome 360/1280 px acceptance.

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

ADR-013 approves a two-dimensional persisted classification:

- normalized `dish_meal_roles` owned by Dish;
- roles `main`, `addition`, `drink`, and `snack`;
- normalized `dish_meal_role_meal_types` owned by each role assignment;
- meal types `breakfast`, `snack`, `lunch`, and `dinner`;
- multiple roles per Dish;
- repeatability per `(dish, role)`;
- compatibility per `(dish, role, meal_type)`;
- no inference from names, recipes, ingredients, or historical placement.

Merged persistence, editor, and readiness slices:

- PR #59: normalized persistence, Alembic `h10001`, API contracts, and atomic classification replacement;
- PR #60: Russian role/meal-type editor, local validation, and responsive browser acceptance;
- PR #61: structured catalogue readiness, blocking required pools, optional recommendations, and Russian warnings.

Required composition slice on PR #63:

- filters every automatic candidate by both role and current meal type;
- requires `main` for breakfast, lunch, and dinner;
- requires `snack` for the snack slot;
- excludes unclassified Dishes and Dishes with archived selected Recipes;
- persists an empty MealSlot and warning instead of silently using an incompatible Dish;
- respects `is_repeatable` for same-day reuse;
- retains deterministic warning fallback when a non-repeatable compatible pool is exhausted;
- keeps MealSlotDish relation identifiers and legacy MealPlanItem compatibility intact.

Quality run #240 is successful for PR #63.

## NEXT

### Deployment catalogue

1. Merge PR #63.
2. Classify the active deployment catalogue explicitly by role and meal type.
3. Verify that every generated project has required breakfast/snack/lunch/dinner coverage.
4. Keep unclassified Dishes manually selectable and excluded from automatic generation.

### Complete meal composition

1. Add optional `addition` and `drink` components to generated main-meal slots.
2. Respect explicitly repeatable additions and drinks.
3. Keep optional gaps as warnings/recommendations rather than required-pool blockers.
4. Implement calendar-day three-day diversity for main dishes.
5. Preserve manual selections as authoritative during regeneration.
6. Persist or deterministically reconstruct warnings for later reads.
7. Add recalculation and end-to-end coverage for multi-component generated slots.

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
