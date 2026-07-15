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
- frontend tests, dependency audit, and production build;
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

### Shopping and documents

- ingredient aggregation;
- package rounding foundation;
- purchase list and checklist;
- transactional refresh and checklist-state preservation;
- PDF/Excel/package export foundations.

### TH-0070 — Critical meal-plan stabilization

Completed by PR #54. Quality passed for backend tests, selected Ruff and strict mypy, Alembic, frontend tests/build/audit, and PostgreSQL backup/restore.

## READY FOR REVIEW

### TH-0065 — Meal Plan Editor UX

Delivered across PR #55 and PR #57:

- compact Russian dish rows;
- explicit replace, add, and confirmed remove flows;
- mutation loading, success, and error feedback;
- collapsible day sections with dish counts;
- full-width editor workspace;
- browser-level React/API acceptance for mutations and errors;
- no-overflow checks and screenshots at desktop, tablet, and 360 px mobile widths.

Quality run #164 is successful. Remaining: Product Owner visual acceptance and squash merge of PR #57.

## IN PROGRESS

### TH-0061 — Guided project preparation

- complete guided Russian preparation workflow;
- connect the corrected editor, purchasing, and export steps;
- verify the complete single-club preparation journey.

## NEXT

### Meal Composition Rules Engine

1. Approve minimal persisted meal-role metadata.
2. Represent main dishes, additions, drinks, and snack-compatible items.
3. Implement composition per breakfast, snack, lunch, and dinner.
4. Implement calendar-day three-day diversity for main dishes.
5. Allow approved repeatable drinks and universal additions.
6. Preserve manual selections as authoritative.
7. Exclude archived-recipe dishes from automatic selection.
8. Persist or reconstruct warnings for later reads.
9. Add unit, service, API, frontend, and recalculation coverage.

No `MealDishRole`, role migration, or role-aware selection is currently implemented.

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
