# TourHub Project Status

Status date: 2026-07-17

## Current phase

TH-0061 guided preparation is functionally complete through Russian purchase and equipment exports. Merged PRs #73–#76 deliver persisted equipment, recalculation, user overrides, and final PDF/Excel/ZIP documents. Draft PR #77 adds persistent single-club branding.

## Verified baseline

- `main`: `51ea7785f12e8d1d30b2768284b6fddbb0117872` — merged PR #76.
- Alembic head on `main`: `h10006`; PR #77 adds `h10007`.
- PR #76 passed exact-head Quality #397 and Document Quality #31 before merge.
- Functional PR #77 head `c3f2c2b767a0751bbf11c214e4f07b21176d0be5` passed Quality #412 and Document Quality #45 before documentation synchronization.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented

### Project, menu, shopping, and equipment

- project workspace, participants, duration, meal boundaries, and role-aware menu generation;
- persisted PurchaseList, PurchaseChecklist, package review, surplus, and purchasing contact;
- persisted recipe equipment requirements and maximum-simultaneous EquipmentList;
- manual equipment rows, quantity overrides, removals, and preservation during every recalculation path;
- transactional refresh after menu, participant, Dish recipe, and direct recipe-equipment changes.

### Russian documents — merged PR #76

- purchase PDF, Excel, and print output;
- equipment PDF and Excel using final visible quantities;
- baseline/source labels and removal-tombstone exclusion;
- five-file project ZIP package;
- Russian download controls and focused Document Quality gates.

### Draft PR #77 — club branding

- singleton club settings persisted through Alembic `h10007`;
- editable club name and optional PNG/JPEG logo;
- server-side MIME, size, image-content, and dimension validation;
- Russian settings UI with preview, removal, save feedback, and 360 px acceptance;
- one cached brand snapshot applied consistently to purchase/equipment PDF, Excel, print, and ZIP contents;
- proportional PDF logo rendering and Excel creator/header/embedded logo metadata.

## Next

1. Complete guided desktop/mobile release acceptance.
2. Add installation and update documentation.
3. Add Docker image/build validation and PostgreSQL migration upgrade/downgrade smoke.
4. Complete the final release workflow.
5. Add invitation-only access only after single-user acceptance.

## Quality debt

- active deployment catalogue data acceptance;
- catalogue-import interaction coverage;
- PostgreSQL migration smoke;
- Docker build validation;
- final release workflow.
