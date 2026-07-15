# TourHub Technical Debt

Status date: 2026-07-15

Technical debt is prioritized by product risk.

## P0 — Release blockers

No open P0 release blockers are recorded after TH-0070 / PR #54.

## P1 — Quality and maintainability

### TD-005 — Ruff backlog

The audited snapshot contained 195 Ruff violations. A critical baseline and selected workflow baseline are enforced. Continue expanding coverage without increasing debt.

### TD-006 — Strict mypy backlog

The audited snapshot contained 74 strict mypy errors. Selected workflow modules, including the menu policy, generator, and catalogue readiness service, are clean and enforced.

### TD-007 — Frontend automated tests

Current coverage includes pure state, command, validation, ordering, summary, feedback, readiness presentation, and responsive-policy helpers.

TH-0065 and PR #57 added real-browser coverage for:

- MealSlot add, replace, and remove operations through React hooks and the shared Axios client;
- explicit removal confirmation;
- Russian success and injected mutation-error feedback;
- no horizontal overflow at desktop, tablet, and 360 px mobile widths;
- desktop, tablet, and mobile screenshot artifacts in Quality CI.

PR #60 adds real-browser coverage for:

- Dish role and meal-type classification through React Query and Axios;
- explicit meal-type requirement for every selected role;
- exact atomic classification payload;
- persisted success and injected backend error feedback;
- lunch-only `main` and multi-meal repeatable drink examples;
- no horizontal overflow at desktop, tablet, and 360 px mobile widths.

PR #61 adds real-browser coverage for:

- blocking Russian readiness warnings for missing required pools;
- non-blocking addition/drink recommendations;
- active and unclassified Dish summaries;
- readiness refresh after role mutation without page reload;
- desktop and 360 px no-overflow screenshots.

Remaining critical coverage:

- project creation and guided preparation;
- active deployment catalogue data acceptance;
- shopping recalculation presentation;
- catalogue import interaction and error rendering;
- final end-to-end release acceptance.

### TD-008 — Continuous Integration

Implemented gates include backend tests, selected Ruff/mypy, Alembic single-head, frontend tests/build/audit, Meal Plan Editor browser acceptance, Dish role/meal compatibility and readiness browser acceptance, and PostgreSQL backup/restore.

Remaining:

- explicit migration upgrade/downgrade smoke against PostgreSQL;
- Docker image/build validation;
- final release-acceptance workflow.

### TD-010 — Documentation and ADR consistency

Canonical current documents and the active task index are synchronized after TH-0070, TH-0065, the role/meal-compatibility design correction, and the minimal readiness policy. ADR-013 supersedes obsolete MealPlanItem-primary wording in ADR-006 and prevents role-only misclassification such as borscht at breakfast. Historical archive documents and duplicate ADR-011 history still require explicit canonical labelling where ambiguity remains.

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

ADR-013 defines persisted role and meal-type compatibility. PR #59 implements:

- normalized `dish_meal_roles` owned by Dish;
- normalized `dish_meal_role_meal_types` owned by each role assignment;
- roles `main`, `addition`, `drink`, and `snack`;
- meal types `breakfast`, `snack`, `lunch`, and `dinner`;
- multiple roles per Dish;
- repeatability per `(dish, role)`;
- compatibility per `(dish, role, meal_type)`;
- Alembic revision `h10001` without heuristic backfill;
- Dish response contracts and atomic classification replacement API;
- duplicate, empty, invalid, incompatible, clearing, and missing-dish API coverage.

PR #60 implements:

- Dish editor controls for roles, meal types, and repeatability;
- local completeness and compatibility validation;
- visible classification summaries;
- browser/API acceptance and responsive screenshots.

PR #61 implements:

- deterministic structured catalogue readiness evaluation;
- required `main` coverage for breakfast/lunch/dinner;
- required `snack` coverage for snack;
- optional addition/drink recommendations;
- archived-recipe exclusion and classification counts;
- Russian warning presentation and browser refresh coverage.

Remaining implementation work:

- explicit classification of the active deployment catalogue;
- role and meal-type composition for breakfast, snack, lunch, and dinner;
- larger candidate thresholds and calendar-day three-day main-dish diversity;
- manual-selection preservation;
- generation-warning persistence or reconstruction;
- preference modes after multi-variant recipes.

Same-day uniqueness, immediate generation warning fallback, and minimal catalogue readiness are no longer open parts of TD-012.

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
