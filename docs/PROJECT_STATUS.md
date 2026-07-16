# TourHub Project Status

Status date: 2026-07-16

## Current phase

TH-0061.5 approved menu rules are complete in `main` through PR #69. TH-0061 guided preparation is active: PR #70 merged the editable purchase checklist, and draft PR #71 adds package-count and package-surplus review.

## Verified baseline

- Current `main`: `3732db5191ab6fcf4fc87725632fbbcc4314625f` — PR #70.
- Alembic head: `h10003`.
- Exact-head Quality #280 passed before PR #69 merge.
- Exact-head Quality #287 passed before PR #70 merge.
- MealSlot and MealSlotDish remain the primary menu-composition model.
- MealPlanItem remains a legacy compatibility path.

## Implemented product areas

### Projects and menu

- project creation, catalogue, workspace, participant count, duration, and meal boundaries;
- role-aware generation using persisted role and meal-type compatibility;
- required `main` and `snack`, optional `addition` and `drink`;
- stable `main → addition → drink` order;
- same-day uniqueness and calendar-day three-day `main` diversity;
- authoritative manual slots across regeneration;
- persisted warning snapshot and later GET responses;
- transactional purchasing recalculation after project, menu, and recipe changes.

Operational follow-up remains explicit classification of the active deployment catalogue.

### Recipes and dishes

- recipe and product catalogues;
- recipe components, quantity modes, notes, archive/restore, and guarded delete;
- transactional CSV import;
- Dish catalogue and active-recipe assignment;
- persisted multi-role classification, compatibility, repeatability, and Russian editor;
- deterministic catalogue-readiness warnings.

### Shopping and documents

Merged foundations:

- ingredient aggregation;
- package-rounding calculation;
- PurchaseList and PurchaseChecklist persistence;
- purchased quantity and checked-state persistence;
- checklist-state preservation during recalculation;
- PDF/Excel/package export foundations;
- PostgreSQL backup/restore CI.

PR #70 merged:

- product names in checklist responses;
- required, purchased, and non-negative remaining quantities;
- rejection of negative purchased quantities;
- editable Russian purchase checklist;
- progress, feedback, responsive layout, and browser acceptance.

Draft PR #71 adds:

- product names in PurchaseList responses;
- total purchase quantity from package size and count;
- non-negative package surplus;
- required quantity, package size, package count, total to buy, and surplus in the project workspace;
- backend API, frontend helper, and combined purchase browser acceptance.

Still required after PR #71:

- optional responsible-person text;
- equipment requirements, aggregation, overrides, and recalculation;
- final Russian documents and release acceptance.

## Quality status

Enforced gates:

- backend pytest, critical/stabilized Ruff, and strict mypy;
- Alembic single-head validation;
- frontend dependency audit, unit tests, production build, and browser acceptance;
- responsive no-overflow checks and screenshots;
- PostgreSQL backup/restore.

Open quality debt:

- complete guided-preparation browser coverage;
- active deployment catalogue acceptance data;
- catalogue-import interaction coverage;
- PostgreSQL migration upgrade/downgrade smoke;
- Docker image/build validation;
- final release-acceptance workflow.

## Immediate sequence

1. Complete exact-head Quality and review for PR #71.
2. Add optional responsible-person text.
3. Implement equipment workflow.
4. Complete final Russian documents and release acceptance.
5. Add invitation-only access only after single-user acceptance.
