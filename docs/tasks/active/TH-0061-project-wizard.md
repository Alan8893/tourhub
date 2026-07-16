# TH-0061 — User Project Preparation Wizard

Status: IN PROGRESS

Last updated: 2026-07-16

## Goal

Create a complete guided Russian scenario for preparing a hiking project from creation through final outputs.

## Completed

- project creation workflow;
- project catalogue and navigation to individual workspaces;
- participant count and duration persistence;
- start date and first/last meal context;
- persistent MealPlan and MealSlot structures;
- role-aware menu generation and realistic diversity rules;
- authoritative manual menu editing and regeneration;
- persisted generation warnings on later reads;
- preparation flow and purchasing projections;
- purchase list and checklist persistence;
- purchased-quantity and checked-state persistence;
- editable project checklist with required, purchased, and remaining quantities through merged PR #70;
- participant and menu mutation recalculation foundations.

## Current implementation slice

### Draft PR #71 — package count and surplus review

- expose product names in purchase-list API responses;
- calculate the total purchase quantity from persisted package size and package count;
- expose non-negative package surplus;
- load the existing project purchase list from the workspace;
- show required quantity, package size, package count, total quantity to buy, and surplus;
- preserve a stacked mobile layout and avoid horizontal overflow at 360 px;
- cover the flow with backend API, frontend helper, and real-browser regressions.

This slice does not change ingredient aggregation, package-rounding calculations, checklist progress, or purchasing recalculation.

## Next slices

1. Add optional responsible-person text.
2. Persist and aggregate recipe equipment requirements.
3. Support manual equipment overrides and recalculation.
4. Complete final Russian PDF/Excel and release acceptance.

## Related decisions

- Project is the preparation aggregate root.
- MealPlan is a persisted business document.
- MealSlot and MealSlotDish are the primary menu composition model.
- Selected dishes are preserved during quantity recalculation.
- Purchase progress remains user-controlled and is preserved during recalculation where products remain present.
- Package review is derived from the persisted PurchaseList rather than recalculated in the browser.
- Multi-user access is deferred until the single-user journey is complete.

## Acceptance criteria

- user can create and locate a project;
- project stores complete preparation context;
- workflow guides the user through menu, shopping, equipment, and exports;
- user can review required, purchased, and remaining quantities in Russian;
- user can review package size, package count, purchase quantity, and surplus;
- purchase changes persist and update visible progress;
- completed workflow is usable on desktop and mobile layouts;
- all backend, frontend, browser, migration, and PostgreSQL quality gates pass.
