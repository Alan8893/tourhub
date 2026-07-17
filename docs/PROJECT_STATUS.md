# TourHub Project Status

Status date: 2026-07-16

## Current phase

TH-0061 guided preparation is nearing completion. PRs #70–#72 completed shopping review, packaging, and the optional purchasing contact. Merged PRs #73–#75 completed persisted equipment requirements, project overrides, recalculation, and direct recipe-mutation refresh. Draft PR #76 completes Russian purchase and equipment document export.

## Verified baseline

- `main`: `d048378c2a4e1d1ac5c57aebe66ba8154fa7eac0` — merged PR #75.
- Alembic head on `main`: `h10006`; PR #76 adds no migration.
- PR #75 passed exact-head Quality #355 before merge.
- Functional PR #76 head `387185880add5a75dfc59071257f6f93cca33471` passed Quality #389 and Document Quality #23 before documentation synchronization.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented

### Project, menu, and shopping

- project workspace, participants, duration, and meal boundaries;
- role-aware menu generation, manual-slot preservation, diversity, and warnings;
- persisted PurchaseList and PurchaseChecklist;
- editable purchase progress, package review, surplus, and optional purchasing contact;
- transactional purchasing recalculation after participant, menu, and recipe changes.

### Equipment — merged PRs #73–#75

- persisted recipe equipment requirements and archived-recipe read-only behavior;
- maximum simultaneous aggregation into one persisted EquipmentList per project;
- manual project rows, quantity overrides, and persisted removals;
- preservation of user decisions during preparation and recalculation;
- refresh after meal-slot edits, Dish recipe changes, participant changes, menu regeneration, and direct recipe-equipment CRUD;
- multi-project transactional fan-out and rollback coverage;
- Russian recipe and project editing UI with desktop and mobile acceptance.

### Draft PR #76 — Russian documents

- Russian purchase PDF and Excel output;
- Russian equipment PDF and Excel output using final user-facing quantities;
- calculated baseline and source labels for calculated, overridden, and manually added rows;
- exclusion of removed equipment rows from export;
- dedicated equipment download API and Russian UI controls;
- full project ZIP package containing purchase PDF, purchase Excel, purchase print, equipment PDF, and equipment Excel;
- focused Document Quality gate for Ruff, strict mypy, and export/API/package tests;
- real-browser validation for five download actions, exact API paths, screenshot, and 360 px no-overflow.

## Next

1. Add club name and logo settings and apply them to document branding.
2. Complete guided-preparation desktop/mobile release acceptance.
3. Add installation and update documentation.
4. Add Docker image/build validation and PostgreSQL migration smoke.
5. Add invitation-only access only after single-user acceptance.

## Quality debt

- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- PostgreSQL migration upgrade/downgrade smoke;
- Docker image/build validation;
- final release workflow.
