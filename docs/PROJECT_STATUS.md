# TourHub Project Status

Status date: 2026-07-16

## Current phase

TH-0061.5 menu rules are complete through PR #69. TH-0061 guided preparation is active: PR #70 delivered the editable purchase checklist, PR #71 delivered package review, PR #72 delivered the optional purchasing contact, and draft PR #73 adds the equipment foundation.

## Verified baseline

- `main`: `3d827a7f9a68fe3d27ac333a4290053e407d3a2d` — PR #72.
- Alembic head on `main`: `h10004`; PR #73 adds `h10005`.
- Exact-head Quality #315 passed before PR #72 merge.
- Exact-head Quality #331 passed for the functional PR #73 head before documentation synchronization.
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
- required, purchased, remaining, package-count, total-purchase, and surplus review;
- editable checked state and purchased quantities;
- optional purchasing contact with trim, clear, length validation, and recalculation preservation;
- responsive Russian UI and browser acceptance.

### Draft PR #73 — equipment foundation

- persisted recipe equipment requirements with add, update, delete, validation, and archived-recipe read-only behavior;
- persisted project EquipmentList generated during project preparation;
- identical equipment summed inside one meal occurrence;
- maximum simultaneous quantity selected across meal occurrences;
- deterministic case-insensitive identity with stable display names;
- repeat generation refreshes one persisted list safely;
- Russian recipe editor and project equipment review;
- backend, unit, build, real-browser, mobile no-overflow, and PostgreSQL coverage.

## Next

1. Complete final exact-head Quality and review for PR #73.
2. Add manual project equipment overrides and preserve them during recalculation.
3. Join equipment refresh to participant, menu, and recipe mutations.
4. Complete final Russian PDF/Excel and release acceptance.
5. Add invitation-only access only after single-user acceptance.

## Quality debt

- complete guided-preparation acceptance;
- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- PostgreSQL migration upgrade/downgrade smoke;
- Docker image/build validation;
- final release workflow.
