# TourHub Current Architecture

Status: Active

Last updated: 2026-07-15

## 1. Purpose

This document is the concise canonical architecture baseline for the implemented MVP. `ARCHITECTURE.md` remains an extended reference. When they conflict, this document and accepted ADRs take precedence.

`PRODUCT_SPEC.md` describes approved target scope. Features marked as deferred here are not yet implemented.

## 2. Deployment

- One installation represents exactly one tourist club.
- Multi-tenant architecture is prohibited.
- The application is a modular monolith.
- The complete local stack starts through `docker compose up --build`.
- PostgreSQL is the production database.
- SQLite may be used only in tests.
- Paid external services are not used.

## 3. Application Boundaries

### Frontend

React, TypeScript, Vite, and Material UI.

Frontend contains presentation, form state, navigation, file selection, and API integration. It does not own quantity calculations, menu generation, shopping aggregation, import validation, or authorization decisions.

### Backend

FastAPI, SQLAlchemy, Alembic, and Pydantic.

Backend currently owns:

- project workflow;
- menu persistence and editing;
- dish and recipe catalogues;
- transactional product and recipe CSV import;
- purchasing recalculation;
- shopping and packaging foundations;
- PDF and Excel generation foundations.

Backend will own authorization, recipe ownership and moderation, equipment, and audit logging when those deferred phases are implemented.

### Engines

Engines receive prepared data and return deterministic results. Engines do not depend on HTTP, React, or database sessions.

## 4. Domain Boundaries

### Access — deferred

Invitation-only access and Administrator, Instructor, and Verified Instructor roles are approved target scope, not current implementation. Backend permission enforcement is required when this phase starts.

### Projects

Project is the preparation root and stores trip dates, participant count, meal boundaries, and links to generated preparation data. `/projects` is the catalogue; `/projects/{id}` is the workspace.

### Nutrition

Owns MealPlan, MealPlanDay, MealSlot, Dish, Recipe, RecipeComponent, generation inputs, and recalculation triggers.

Dish and Recipe are separate. Current persistence stores one selected `Dish.recipe_id`. Multiple recipe variants, ownership, and preference modes are future target work.

### Catalog import

CSV import has preview and apply operations. Parsing, validation, duplicate handling, references, and transaction boundaries belong to Backend. Invalid input must not create partial catalogue data.

### Shopping

Owns ingredient aggregation, package rounding, purchased quantities, checklist state, comments, and category. Participant changes, MealSlot mutations, and Dish recipe replacement refresh affected persisted projections transactionally.

### Equipment — planned

Requirements will originate from recipes and be aggregated by maximum simultaneous need. Manual overrides will be allowed.

### Documents

Owns Russian PDF and Excel export foundations. Final templates and club branding remain incomplete.

### Audit — deferred

Audit logging begins after identity and roles exist.

## 5. Recalculation Contract

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

## 6. Persistence Evolution

- Existing working models evolve incrementally.
- Alembic must have exactly one head.
- Applied migrations are not rewritten when real data may exist.
- Public API placeholders are prohibited.
- Legacy compatibility requires a verified consumer or migration plan.
- One-recipe-per-Dish persistence must not be described as multi-variant until a migration and selection contract exist.

## 7. Security Rules

- Club data is not transmitted to external paid services.
- Multi-user permissions must be enforced in Backend when introduced.
- Alcohol prohibition remains approved product scope but still needs centralized API and import enforcement.

## 8. Future Domains

Not part of the current single-club MVP:

- participant profiles and personal data;
- routes and GPX;
- logistics and load distribution;
- warehouse balances and issue workflow;
- price aggregator integration;
- multi-tenant support.

## 9. Change Rule

Any change to deployment boundaries, domain ownership, persistence strategy, stack, or MVP scope requires:

1. Product Owner approval when product or stack is affected;
2. an ADR;
3. synchronized documentation;
4. migration and compatibility analysis;
5. tests.

See ADR-012 and `PRODUCT_SPEC.md`.