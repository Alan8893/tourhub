# TourHub Project Status

Status date: 2026-07-16

## Current phase

TH-0061.5 remains active. Persisted classification and production role-aware generation are merged; the open stack now contains documentation synchronization, calendar-day `main` diversity, and manual-slot preservation during regeneration.

Merged delivery chain:

- PR #59 — normalized Dish roles and role-specific meal-type compatibility;
- PR #60 — Russian catalogue editor for roles, meal types, and repeatability;
- PR #61 — deterministic catalogue-readiness API and visible Russian warnings;
- PR #62 — responsive mobile navigation drawer;
- PR #64 — role- and meal-type-aware project meal-plan generation.

Open stack:

- PR #65 — canonical documentation synchronization after PR #64;
- PR #66 — calendar-day three-day diversity for `main` dishes;
- PR #67 — preservation of manually edited MealSlots during regeneration.

The Product Owner verified the updated local deployment after PR #64. Automatic generation uses only explicitly classified, active-recipe dishes, while manual choices remain available independently of automatic classification.

## Verified baseline

- Current `main` includes PR #64 at squash commit `cdc211ed6bbcc12779c28d692a312022d297cf01`.
- `main` currently has Alembic head `h10001`; stacked PR #67 adds `h10002` for the manual-slot marker.
- Quality run #254 passed on the exact PR #64 head with 175 backend tests, Ruff, strict mypy, Alembic validation, frontend tests/build/browser acceptance, and PostgreSQL backup/restore.
- Documentation PR #65 is Ready for review, mergeable, and has successful exact-head Quality #256.
- Diversity PR #66 is Ready for review, mergeable, and has successful exact-head Quality #264.
- MealSlot and MealSlotDish are the primary menu-composition persistence model.
- MealPlanItem remains a legacy compatibility path.
- MealSlot API responses expose persisted relation identifiers separately from source `dish_id` values.
- Docker Compose, automatic migrations, LAN-safe same-origin routing, mobile navigation, project creation, menu editing, purchasing recalculation, and export foundations are operational.

## Implemented product areas

### Projects

- project creation and catalogue;
- participant count, duration, first meal, and last meal;
- backend meal-boundary validation;
- project workspace routing;
- participant-count purchasing recalculation with rollback;
- same-origin browser routing for LAN clients.

Still required:

- complete the guided Russian preparation workflow;
- equipment-dependent recalculation;
- invitation-only access after single-user acceptance.

### Meal plan

- persisted MealPlan, MealPlanDay, MealSlot, and MealSlotDish;
- first/last meal scheduling and one-day support;
- multiple dishes per MealSlot;
- add, replace, and remove operations;
- corrected MealSlotDish identifier contract;
- compact responsive Russian editor;
- normalized Dish role and meal-type compatibility;
- catalogue-readiness evaluation and visible warnings;
- automatic filtering by both persisted role and current meal type;
- required `main` for breakfast/lunch/dinner and required `snack` for snack;
- optional compatible `addition` and `drink` selection;
- stable composition order `main → addition → drink`;
- repeatability evaluated per `(dish, role)` assignment;
- same-day uniqueness for non-repeatable assignments;
- archived-recipe and unclassified dishes excluded from automatic generation;
- explicit required-pool warnings instead of hidden incompatible fallback;
- generated compositions persisted through MealSlot/MealSlotDish and compatibility MealPlanItem rows;
- transactional purchasing recalculation after MealSlot edits.

PR #66 adds:

- trip-calendar-day tracking in the pure selection context;
- a rolling three-day diversity window only for non-repeatable `main` assignments;
- day-one `main` reuse on day four;
- repeatable `main` bypass of the diversity restriction;
- deterministic empty required slots and warnings when the diversity-eligible pool is exhausted;
- pure engine, service, persistence, and public API regressions.

PR #67 adds:

- persisted `MealSlot.is_manually_edited` through Alembic revision `h10002`;
- manual marking after successful add, replace, or remove, including a fully emptied slot;
- regeneration in place for an existing project MealPlan rather than duplicate-plan creation;
- exact preservation of marked slots while unmarked slots are regenerated;
- preservation of unclassified manual dishes without guessing a role;
- no automatic required-role warning for an authoritative preserved slot;
- continued separation of warning persistence into the next slice.

Still required for TH-0061.5 after PR #67:

- maintain and complete explicit classification of the active deployment catalogue;
- persistence or deterministic reconstruction of generation warnings for later GET responses;
- larger diversity thresholds and future preference modes only after approved product requirements.

### Dishes and recipes

- Dish and Recipe separation;
- dish catalogue, create, rename, and active-recipe assignment;
- persisted multi-role classification with per-role meal compatibility and repeatability;
- atomic classification replacement API;
- Russian role/meal-type editor;
- active/classified/unclassified readiness counts;
- archived-recipe exclusion from readiness and automatic generation candidates;
- recipe components, quantity modes, notes, archive/restore, and guarded deletion;
- transactional CSV import;
- purchasing recalculation after Dish recipe replacement.

Still required:

- impact preview before recipe replacement;
- product update/delete;
- preparation, equipment, dietary, season, and category metadata;
- centralized alcohol-prohibition enforcement;
- multiple recipe variants and ownership after multi-user mode.

### Shopping and documents

- ingredient aggregation;
- shopping list and purchase checklist;
- package-rounding foundation;
- transactional recalculation after participant, MealSlot, and Dish recipe changes;
- checklist-state preservation;
- PDF/Excel/package export foundations;
- PostgreSQL backup/restore scripts and CI smoke test.

Still required:

- complete package and remainder presentation;
- responsible-person field;
- equipment pipeline;
- final Russian templates and club branding.

## Quality status

Enforced gates:

- backend tests;
- critical and selected expanded Ruff baselines;
- selected strict mypy baseline;
- Alembic single-head validation;
- frontend Node tests and dependency audit;
- TypeScript production build;
- Meal Plan Editor browser acceptance;
- Dish role/meal-compatibility browser acceptance;
- catalogue-readiness browser acceptance;
- responsive application navigation browser acceptance;
- desktop, tablet, and 360 px no-overflow checks and screenshots;
- PostgreSQL backup/restore smoke test.

PR #66 regression scope verifies calendar-day diversity, repeatable-main bypass, pool exhaustion, service mapping, persistence alignment, and public API behavior.

PR #67 regression scope verifies:

- manual mutation marking for add, replace, and remove;
- authoritative preservation of non-empty and empty manual slots;
- no role inference for an unclassified manual dish;
- suppression of irrelevant automatic warnings for preserved slots;
- reuse of one project MealPlan across regeneration;
- persistence of the regenerated composition through a subsequent GET;
- unchanged automatic generation for unmarked slots.

Open quality debt:

- guided preparation browser coverage;
- active deployment catalogue acceptance data;
- shopping and catalogue-import browser coverage;
- explicit PostgreSQL migration upgrade/downgrade smoke;
- Docker image/build CI validation;
- final release-acceptance workflow.

## Active tasks

- TH-0061 — guided project preparation journey;
- TH-0061.5 — finish the open diversity/regeneration stack, then warning lifecycle.

## Immediate sequence

1. Keep the active catalogue explicitly classified and verify readiness on real deployment data.
2. Review and merge PR #65, #66, and #67 only by explicit Product Owner command and in dependency order.
3. Persist or deterministically reconstruct generation warnings for later reads.
4. Complete the guided preparation, packaging, equipment, and export acceptance workflow.
5. Introduce invitation-only access and roles only after single-user acceptance.
