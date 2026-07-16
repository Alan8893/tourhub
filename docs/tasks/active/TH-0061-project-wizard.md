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
- participant and menu mutation recalculation foundations.

## Current implementation slice

### Draft PR #70 — editable project purchase checklist

- expose product names in purchase-checklist API responses;
- expose required, purchased, and non-negative remaining quantities;
- reject negative purchased quantities;
- load the existing project checklist from the workspace;
- edit purchased quantity through the existing PATCH endpoint;
- mark and unmark a position as purchased;
- show checked progress and Russian loading/error/success feedback;
- preserve a stacked mobile layout and avoid horizontal overflow at 360 px;
- cover the flow with backend API, frontend state, and real-browser regressions.

This slice does not change ingredient aggregation or package-rounding calculations.

## Next slices

1. Present package count and package surplus/remainder clearly.
2. Add optional responsible-person text.
3. Persist and aggregate recipe equipment requirements.
4. Support manual equipment overrides and recalculation.
5. Complete final Russian PDF/Excel and release acceptance.

## Related decisions

- Project is the preparation aggregate root.
- MealPlan is a persisted business document.
- MealSlot and MealSlotDish are the primary menu composition model.
- Selected dishes are preserved during quantity recalculation.
- Purchase progress remains user-controlled and is preserved during recalculation where products remain present.
- Multi-user access is deferred until the single-user journey is complete.

## Acceptance criteria

- user can create and locate a project;
- project stores complete preparation context;
- workflow guides the user through menu, shopping, equipment, and exports;
- user can review required, purchased, and remaining quantities in Russian;
- purchase changes persist and update visible progress;
- completed workflow is usable on desktop and mobile layouts;
- all backend, frontend, browser, migration, and PostgreSQL quality gates pass.
