# TourHub Project Status

Status date: 2026-07-17

## Current phase

TH-0061 guided preparation is in its final stacked review sequence. PR #77 adds persistent single-club branding. Draft PR #78 is stacked on #77 and completes guided desktop/mobile release acceptance, including persistence restoration after reload.

## Verified baseline

- `main`: `51ea7785f12e8d1d30b2768284b6fddbb0117872` — merged PR #76.
- Alembic head on `main`: `h10006`; PR #77 adds `h10007`; PR #78 adds no migration.
- PR #77 exact head `317d3b013e0a24c224c8b291e06f49bef349305d` passed Quality #416 and Document Quality #49 and is Ready.
- Functional PR #78 head `b247b2d7c2dd38c9874e92c524a66f25b293e3bf` passed Quality #421, Document Quality #54, and Guided Release Acceptance #5 before documentation synchronization.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented

### Guided project preparation

- project creation, participants, duration, meal boundaries, and role-aware menu generation;
- persisted PurchaseList, PurchaseChecklist, package review, surplus, and purchasing contact;
- persisted equipment requirements, maximum-simultaneous aggregation, manual rows, overrides, and removals;
- transactional refresh after menu, participant, Dish recipe, and direct recipe-equipment changes;
- Russian purchase/equipment PDF, Excel, print, and five-file ZIP output through merged PR #76.

### PR #77 — club branding

- singleton club settings persisted through Alembic `h10007`;
- editable club name and optional validated PNG/JPEG logo;
- one cached brand snapshot applied to purchase/equipment PDF, Excel, print, and ZIP;
- Russian settings UI with preview, removal, feedback, screenshot, and 360 px acceptance.

### Draft PR #78 — guided release acceptance

- read-only persisted preparation-status API;
- workflow state restoration after browser reload without repeated preparation;
- equipment required before project and documents are marked complete;
- missing purchase lists treated as unprepared state instead of server error;
- remaining project-workspace text localized to Russian;
- full browser flow: create project → generate menu → prepare purchase/checklist/equipment → reload → download branded ZIP;
- exact request assertions, desktop flow, mobile screenshot, and 360 px no-overflow;
- focused Guided Release Acceptance workflow with Ruff, strict mypy, API tests, browser evidence, and failure diagnostics.

## Next

1. Merge PR #77, then retarget or rebase PR #78 onto `main` and rerun exact-head checks.
2. Add installation and update documentation.
3. Add Docker image/build validation and PostgreSQL migration upgrade/downgrade smoke.
4. Complete the final release workflow.
5. Add invitation-only access only after single-user acceptance.

## Quality debt

- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- PostgreSQL migration smoke;
- Docker build validation;
- installation/update runbook;
- final release workflow.
