# TourHub Project Status

Status date: 2026-07-16

## Current phase

TH-0061 guided preparation is active. PRs #70–#72 completed shopping review, packaging, and the purchasing contact. Merged PRs #73 and #74 delivered persisted equipment aggregation, project editing, override preservation, and recalculation after menu and participant changes. Draft PR #75 closes the remaining recipe-equipment recalculation gap.

## Verified baseline

- `main`: `4bde39c480776d46bf25894cb77602a4e1adb0cd` — merged PR #74.
- Alembic head on `main`: `h10006`.
- PR #74 passed exact-head Quality #350 before merge.
- Functional PR #75 head `4e6f6a09e11435199e5c7fcb59c444f642d25388` passed Quality #353 before documentation synchronization.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented

### Project, menu, and shopping

- project workspace, participants, duration, and meal boundaries;
- role-aware menu generation, manual-slot preservation, diversity, and warnings;
- persisted PurchaseList and PurchaseChecklist;
- editable purchase progress, package review, surplus, and purchasing contact;
- transactional purchasing recalculation after participant, menu, and recipe changes.

### Equipment through merged PR #74

- persisted recipe equipment requirements through Alembic `h10005`;
- maximum simultaneous aggregation into one persisted EquipmentList per project;
- separate calculated baseline and final user-controlled quantity through `h10006`;
- manual additions, removals, and quantity overrides;
- preservation of explicit user decisions during repeated preparation;
- refresh after meal-slot edits, Dish recipe changes, participant changes, and full menu regeneration;
- Russian editing UI with calculated, manual, and overridden state;
- API, unit, build, browser, screenshot, mobile, and PostgreSQL coverage.

### Draft PR #75 — recipe requirement recalculation

- refresh all already prepared EquipmentLists using a recipe after requirement POST, PUT, or DELETE;
- perform requirement mutation and every derived-list refresh in one transaction;
- preserve project overrides, removals, and manual rows during the refresh;
- avoid creating EquipmentLists for projects that were never prepared;
- cover multi-project fan-out and rollback on refresh failure;
- enforce the new recalculation service in stabilized Ruff and strict mypy gates.

## Next

1. Include equipment in the final Russian PDF and Excel outputs.
2. Complete guided-preparation and release acceptance.
3. Add club branding and installation/update documentation.
4. Add invitation-only access only after single-user acceptance.

## Quality debt

- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- PostgreSQL migration upgrade/downgrade smoke;
- Docker image/build validation;
- final release workflow.
