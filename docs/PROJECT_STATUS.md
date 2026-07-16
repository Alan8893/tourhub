# TourHub Project Status

Status date: 2026-07-16

## Current phase

TH-0061.5 menu rules are complete through PR #69. TH-0061 guided preparation is active: PR #70 delivered the editable purchase checklist, PR #71 delivered package-count and surplus review, and draft PR #72 adds an optional purchasing contact.

## Verified baseline

- `main`: `ed2ab62a70cefbd41425e9cdbaab0f81a6777298` — PR #71.
- Alembic head on `main`: `h10003`; PR #72 adds `h10004`.
- Exact-head Quality #287 passed before PR #70 merge.
- Exact-head Quality #296 passed before PR #71 merge.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented

### Project and menu

- project workspace, participants, duration, and meal boundaries;
- persisted Dish roles, meal compatibility, repeatability, and catalogue readiness;
- role-aware menu generation with diversity, manual-slot preservation, and persisted warnings;
- transactional purchasing recalculation after project, menu, and recipe changes.

### Shopping and packaging

- ingredient aggregation and package rounding;
- persisted PurchaseList and PurchaseChecklist;
- required, purchased, and remaining quantity review;
- editable checked state and purchased quantities;
- package size, package count, total purchase quantity, and non-negative surplus;
- responsive Russian UI and browser acceptance.

Draft PR #72 adds:

- nullable purchasing contact on PurchaseList through Alembic `h10004`;
- GET/PATCH API with trim, clear, and 255-character validation;
- preservation when purchase-list items are recalculated;
- save/clear UI and dedicated browser coverage.

## Next

1. Complete exact-head Quality and review for PR #72.
2. Implement equipment requirements, aggregation, overrides, and recalculation.
3. Complete final Russian PDF/Excel and release acceptance.
4. Add invitation-only access only after single-user acceptance.

## Quality debt

- complete guided-preparation acceptance;
- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- PostgreSQL migration upgrade/downgrade smoke;
- Docker image/build validation;
- final release workflow.
