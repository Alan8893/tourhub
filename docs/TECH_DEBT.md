# TourHub Technical Debt

Status date: 2026-07-16

Technical debt is prioritized by product risk.

## P0 — Release blockers

No open P0 release blockers are recorded after TH-0070 / PR #54.

## P1 — Quality and maintainability

### TD-005 — Ruff backlog

The audited snapshot contained 195 Ruff violations. Critical and selected workflow baselines are enforced. Continue expanding coverage without increasing debt.

### TD-006 — Strict mypy backlog

The audited snapshot contained 74 strict mypy errors. Selected workflow modules, including meal policy, role-aware generator, MealPlanService mapping, and catalogue readiness, are clean and enforced.

### TD-007 — Frontend and browser automated tests

Current coverage includes pure state, command, validation, ordering, summary, feedback, readiness presentation, and responsive-policy helpers.

Real-browser coverage now includes:

- MealSlot add, replace, and remove operations;
- explicit removal confirmation;
- Russian success and injected mutation-error feedback;
- Dish role and meal-type classification through React Query and Axios;
- exact atomic classification payload;
- readiness warning refresh after role mutation;
- responsive mobile navigation closed by default, open on demand, and closed after navigation;
- no horizontal overflow at desktop, tablet, and 360 px mobile widths;
- stable screenshot artifacts.

PR #64 adds backend/persistence/API integration coverage rather than a new frontend workflow. It verifies real project generation with persisted ORM roles and distinguishes `MealSlotDish.id` from source `dish_id`.

Remaining critical coverage:

- guided project preparation;
- active deployment catalogue acceptance data;
- shopping recalculation presentation;
- catalogue import interaction and error rendering;
- final end-to-end release acceptance.

### TD-008 — Continuous Integration

Implemented gates include backend tests, selected Ruff/mypy, Alembic single-head, frontend tests/build/audit, all browser acceptance suites, and PostgreSQL backup/restore.

Remaining:

- explicit migration upgrade/downgrade smoke against PostgreSQL;
- Docker image/build validation;
- final release-acceptance workflow.

### TD-010 — Documentation and ADR consistency

Canonical status, roadmap, context, domain, architecture, and active TH-0061.5 documentation are synchronized after PR #64. ADR-013 remains the accepted source for persisted role and meal-type ownership. ADR-006 is superseded where it described MealPlanItem as primary.

Historical archive documents and duplicate ADR-011 history still require explicit canonical labelling where ambiguity remains.

### TD-024 — Legacy MealPlanItem compatibility

MealSlot is primary. MealPlanItem remains persisted for compatibility and increases mapping and recalculation complexity.

Required later:

- identify remaining consumers;
- verify legacy-only recalculation behavior;
- create a migration/removal plan;
- remove duplicate persistence only through an approved compatibility change.

## P2 — Product completion debt

### TD-002 — Multi-user authorization baseline

Invitation-only registration, secure local authentication, roles, recipe ownership, and administration are deferred until the single-user workflow is accepted.

### TD-011 — Recipe ownership and moderation

Remaining work covers CLUB/PERSONAL ownership, multiple recipe variants, publication review, and verified-instructor moderation.

### TD-012 — Meal composition and diversity

Implemented through PR #59, #60, #61, and #64:

- normalized `dish_meal_roles` owned by Dish;
- normalized `dish_meal_role_meal_types` owned by each role assignment;
- roles `main`, `addition`, `drink`, and `snack`;
- meal types `breakfast`, `snack`, `lunch`, and `dinner`;
- multiple roles per Dish;
- repeatability per `(dish, role)`;
- compatibility per `(dish, role, meal_type)`;
- Alembic revision `h10001` without heuristic backfill;
- Dish response contracts and atomic classification replacement API;
- Russian role/meal-type management UI;
- deterministic structured catalogue readiness;
- required `main` coverage for breakfast/lunch/dinner and `snack` coverage for snack;
- optional addition/drink recommendations;
- archived-recipe exclusion and classification counts;
- role- and meal-type-aware production generation;
- optional compatible `addition` and `drink` composition;
- stable composition persistence order;
- explicit required-pool warnings without incompatible fallback;
- exclusion of unclassified and archived-recipe dishes from automatic selection;
- same-day uniqueness with per-role repeatability exceptions;
- pure, service, persistence, and public API integration coverage.

Remaining implementation work:

- maintain and complete explicit classification of the active deployment catalogue;
- larger candidate thresholds and calendar-day three-day `main` diversity;
- manual-selection preservation during regeneration;
- generation-warning persistence or deterministic reconstruction;
- preference modes after multi-variant recipes.

Minimal readiness, role-aware composition, optional repeatable roles, archived-recipe filtering, and immediate warnings are no longer open parts of TD-012.

### TD-013 — Equipment domain completion

Persist recipe equipment requirements, aggregate maximum simultaneous need, support manual overrides, and join equipment to transactional recalculation.

### TD-014 — Export templates and branding

Complete Russian PDF/Excel templates and load club logo and name from settings.

### TD-015 — Audit log

Record actor/action/time metadata when multi-user access is introduced.

### TD-019 — Dish recipe change impact preview

Show how many existing plans and purchasing projections will be recalculated before recipe replacement.

### TD-020 — Alcohol prohibition enforcement

Apply the prohibition consistently in backend product, recipe, dish, and import validation with regression tests.

### TD-025 — Complete Product CRUD

Product currently supports list and create. Update and guarded delete remain unimplemented.

## Completed history

- TD-001 — accidental public API placeholders removed.
- TD-003 — participant, MealSlot, and Dish recipe purchasing refresh implemented transactionally.
- TD-004 — local stack and primary workflow verified during stabilization.
- TD-009 — dependency audit passes at moderate severity.
- TD-016 — backup/restore scripts and CI smoke test implemented.
- TD-017 — Meal Plan Editor UX and responsive browser acceptance completed by TH-0065 / PR #57.
- TD-018 — dish catalogue and active-recipe assignment implemented.
- TD-021 — MealSlot relation identifiers and `/dishes` frontend contract repaired by PR #54.
- TD-022 — invalid selection-count pseudo cooldown removed by PR #54.
- TD-023 — backend meal-boundary authority and regression tests delivered by PR #54.
