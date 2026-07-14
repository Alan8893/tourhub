# TourHub Current Architecture

Status: Active

Last updated: 2026-07-14

## 1. Purpose

This document is the concise canonical architecture baseline for the current MVP. `ARCHITECTURE.md` remains an extended reference. When they conflict, this document and accepted ADRs take precedence.

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

Frontend contains presentation, form state, navigation, and API integration. It does not own business rules, authorization decisions, quantity calculations, menu generation, shopping aggregation, or document calculations.

### Backend

FastAPI, SQLAlchemy, Alembic, and Pydantic.

Backend is the only source of business truth and owns:

- authorization and permissions;
- project workflow;
- menu generation and editing;
- recipe selection and moderation;
- recalculation;
- shopping and packaging;
- equipment requirements;
- audit logging;
- PDF and Excel generation.

### Engines

Engines receive prepared data and return deterministic results. Engines do not depend on HTTP, React, or database sessions.

## 4. Domain Boundaries

### Access

Invitation-only registration and roles:

- Administrator;
- Instructor;
- Verified Instructor.

Permissions are enforced in Backend.

### Projects

Project is the preparation root and stores trip dates, participant count, meal boundaries, and links to generated preparation data.

### Nutrition

Owns MealPlan, MealPlanDay, MealSlot, Dish, Recipe, RecipeComponent, generation, diversity rules, recipe preferences, and recalculation inputs.

Dish and Recipe are separate. One Dish may have multiple Recipe variants.

### Shopping

Owns ingredient aggregation, package rounding, purchased quantities, remainder, checklist state, comments, category, and optional responsible person.

### Equipment

Requirements originate from recipes. Identical equipment is aggregated by maximum simultaneous requirement. Manual overrides are allowed.

### Documents

Owns Russian PDF and Excel exports. Club name and logo come from system settings.

### Audit

Records actor, action, timestamp, and safe metadata for project, menu, recipe, publication, user, role, and invitation changes.

## 5. Recalculation Contract

Participant-count and menu changes preserve selected dishes and recalculate dependent quantities:

```text
Project / MealSlot
        ↓
Recipe Components
        ↓
Ingredient Totals
        ↓
Packages
        ↓
Shopping
        ↓
Equipment
```

The calculation must be transactional or leave the previous valid state unchanged.

## 6. Persistence Evolution

- Existing working models evolve incrementally.
- Alembic must have exactly one head.
- Applied migrations are not rewritten when real data may exist.
- Public API placeholders are prohibited.
- Legacy compatibility is preserved only when it has a verified consumer or migration plan.

## 7. Security Rules

- No open registration.
- Passwords, tokens, invitation secrets, and sensitive values are never logged.
- Alcohol prohibition is enforced in Backend validation.
- Club data is not transmitted to external paid services.
- Authorization cannot rely on hidden frontend controls.

## 8. Future Domains

Not part of MVP:

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
