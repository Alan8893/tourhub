# TourHub Project Status

Status date: 2026-07-16

## Current phase

TH-0061 guided preparation is active. PRs #70–#72 completed shopping review, packaging, and the optional purchasing contact. Merged PR #73 delivered persisted recipe equipment requirements and maximum simultaneous aggregation. Draft PR #74 completes project-level equipment editing and override preservation.

## Verified baseline

- `main`: `cf4d39b9d7834e13763a4a02b8b2a13f25e44f5a` — merged PR #73.
- Alembic head on `main`: `h10005`; PR #74 adds `h10006`.
- PR #73 passed exact-head Quality #334 before merge.
- Functional PR #74 head `cef66b99c4546805cffc0ad0e445e0fe8048e86c` passed Quality #349 before documentation synchronization.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented

### Project, menu, and shopping

- project workspace, participants, duration, and meal boundaries;
- role-aware menu generation, manual-slot preservation, diversity, and warnings;
- persisted PurchaseList and PurchaseChecklist;
- editable purchase progress, package review, surplus, and optional purchasing contact;
- transactional purchasing recalculation after participant, menu, and recipe changes.

### Equipment foundation — merged PR #73

- persisted recipe equipment requirements through Alembic `h10005`;
- validated CRUD and archived-recipe read-only behavior;
- one persisted EquipmentList per project;
- identical equipment summed within one meal occurrence;
- maximum simultaneous quantity selected across occurrences;
- Russian recipe editor and project review UI;
- backend, frontend, browser, mobile, and PostgreSQL coverage.

### Draft PR #74 — equipment overrides and recalculation

- separate calculated baseline from the final user-facing quantity through Alembic `h10006`;
- add manual project equipment rows;
- edit final quantities and mark calculated rows as overridden;
- persist removals of calculated rows without losing source calculations;
- preserve manual additions, removals, and quantity overrides during repeated preparation;
- refresh existing EquipmentList after meal-slot edits, Dish recipe changes, participant changes, and full menu regeneration;
- provide Russian editing controls with calculated/manual/overridden labels;
- cover CRUD interactions, refetch, screenshot, and 360 px no-overflow in a real browser;
- enforce the new override and regeneration modules in stabilized Ruff and strict mypy gates.

## Next

1. Refresh affected project equipment lists immediately after direct recipe-equipment requirement mutations.
2. Include equipment in the final Russian PDF and Excel outputs.
3. Complete guided-preparation and release acceptance.
4. Add invitation-only access only after single-user acceptance.

## Quality debt

- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- PostgreSQL migration upgrade/downgrade smoke;
- Docker image/build validation;
- final release workflow.
