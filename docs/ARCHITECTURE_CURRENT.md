# TourHub Current Architecture

Status: Active

Last updated: 2026-07-16

## 1. Purpose

This document is the concise canonical architecture baseline for the implemented MVP. `ARCHITECTURE.md` remains an extended reference. When they conflict, this document and accepted ADRs take precedence.

`PRODUCT_SPEC.md` describes approved target scope. Features marked as deferred here are not yet implemented.

## 2. Deployment

- One installation represents exactly one tourist club.
- Multi-tenant architecture is prohibited.
- The application is a modular monolith.
- The complete local stack starts through `docker compose up -d --build`.
- PostgreSQL is the production database.
- SQLite may be used only in tests.
- Paid external services are not used.

## 3. Application boundaries

### Frontend

React, TypeScript, Vite, Material UI, TanStack Query, and React Router.

Frontend contains presentation, form state, navigation, file selection, and API integration. It does not own quantity calculations, menu generation, shopping aggregation, import validation, or authorization decisions.

The application layout uses a temporary drawer on mobile and a permanent sidebar on larger screens.

### Backend

FastAPI, SQLAlchemy, Alembic, Pydantic, and deterministic engines.

Backend currently owns:

- project workflow and meal-boundary validation;
- menu persistence, editing, and generation;
- Dish role and meal-type classification validation;
- catalogue-readiness evaluation;
- dish and recipe catalogues;
- transactional product and recipe CSV import;
- purchasing recalculation;
- shopping and packaging foundations;
- PDF and Excel generation foundations.

Backend will own authorization, recipe ownership and moderation, equipment, and audit logging when those deferred phases are implemented.

### Engines

Engines receive prepared data and return deterministic results. Engines do not depend on HTTP, React, or database sessions.

MealPlanService prepares active Dish data, excludes archived recipes, maps persisted role assignments into engine inputs, and invokes the generator in explicit role-aware mode.

## 4. Domain boundaries

### Access — deferred

Invitation-only access and Administrator, Instructor, and Verified Instructor roles are approved target scope, not current implementation. Backend permission enforcement is required when this phase starts.

### Projects

Project is the preparation root and stores trip dates, participant count, meal boundaries, and links to generated preparation data. `/projects` is the catalogue; `/projects/{id}` is the workspace.

### Nutrition

Owns MealPlan, MealPlanDay, MealSlot, MealSlotDish, Dish, DishMealRole, DishMealRoleMealType, Recipe, RecipeComponent, generation inputs, and recalculation triggers.

MealSlot and MealSlotDish are the primary menu-composition persistence model. MealPlanItem remains a legacy compatibility path.

Dish and Recipe are separate. Current persistence stores one selected `Dish.recipe_id`. Multiple recipe variants, ownership, and preference modes are future target work.

Dish classification follows ADR-013:

```text
dish_meal_roles
  (dish_id, role) primary key
  is_repeatable

 dish_meal_role_meal_types
  (dish_id, role, meal_type) primary key
```

Role compatibility is owned by Dish, not Recipe or MealSlotDish. Manual MealSlotDish assignments remain authoritative.

Automatic composition policy:

- breakfast/lunch/dinner require compatible `main`;
- snack requires compatible `snack`;
- compatible `addition` and `drink` are optional;
- composition order is `main → addition → drink`;
- repeatability belongs to the selected `(dish, role)` assignment;
- unclassified and archived-recipe dishes are not automatic candidates;
- missing required pools produce explicit warnings rather than an incompatible fallback.

Calendar-day three-day diversity and regeneration-preservation rules remain future extensions of the same engine boundary.

### Catalogue import

CSV import has preview and apply operations. Parsing, validation, duplicate handling, references, and transaction boundaries belong to Backend. Invalid input must not create partial catalogue data.

### Shopping

Owns ingredient aggregation, package rounding, purchased quantities, checklist state, comments, and category. Participant changes, MealSlot mutations, and Dish recipe replacement refresh affected persisted projections transactionally.

### Equipment — planned

Requirements will originate from recipes and be aggregated by maximum simultaneous need. Manual overrides will be allowed.

### Documents

Owns Russian PDF and Excel export foundations. Final templates and club branding remain incomplete.

### Audit — deferred

Audit logging begins after identity and roles exist.

## 5. Recalculation contract

Implemented triggers preserve selected menu structure and recalculate purchasing data:

```text
Participant count / MealSlot / Dish.recipe_id
        ↓
Recipe Components and legacy ingredients
        ↓
Ingredient Totals
        ↓
Packages
        ↓
Purchase List and Checklist
```

Equipment joins this chain after equipment persistence exists.

Recalculation must be transactional or leave the previous valid state unchanged. Checklist state is preserved for products that remain after refresh.

## 6. Persistence evolution

- Existing working models evolve incrementally.
- Alembic must have exactly one head; the current head is `h10001`.
- Applied migrations are not rewritten when real data may exist.
- Public API placeholders are prohibited.
- Legacy compatibility requires a verified consumer or migration plan.
- One-recipe-per-Dish persistence must not be described as multi-variant until a migration and selection contract exist.
- Role or meal-type metadata must never be inferred from names, ingredients, recipes, or historical placement.

## 7. Security rules

- Club data is not transmitted to external paid services.
- Multi-user permissions must be enforced in Backend when introduced.
- Alcohol prohibition remains approved product scope but still needs centralized API and import enforcement.

## 8. Future domains

Not part of the current single-club MVP:

- participant profiles and personal data;
- routes and GPX;
- logistics and load distribution;
- warehouse balances and issue workflow;
- price aggregator integration;
- multi-tenant support.

## 9. Change rule

Any change to deployment boundaries, domain ownership, persistence strategy, stack, or MVP scope requires:

1. Product Owner approval when product or stack is affected;
2. an ADR;
3. synchronized documentation;
4. migration and compatibility analysis;
5. tests.

See ADR-012, ADR-013, and `PRODUCT_SPEC.md`.
