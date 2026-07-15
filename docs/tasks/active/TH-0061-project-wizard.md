# TH-0061 — User Project Preparation Wizard

Status: IN PROGRESS

## Goal

Create a complete guided user scenario for preparing a hiking project from creation through final outputs.

## Completed

- project creation workflow;
- project catalogue and navigation to individual workspaces;
- participant count and duration persistence;
- start date and first/last meal context;
- persistent MealPlan and MealSlot structures;
- editable dishes in meal slots;
- preparation flow and purchasing projections;
- participant and menu mutation recalculation foundations.

## Current

Complete the guided Russian workflow after menu editing:

- meal composition and diversity rules;
- clear packaging and shopping review;
- equipment preparation;
- final exports and acceptance UX.

## Related decisions

- Project is the preparation aggregate root.
- MealPlan is a persisted business document.
- Selected dishes are preserved during quantity recalculation.
- Multi-user access is deferred until the single-user journey is complete.

## Acceptance criteria

- user can create and locate a project;
- project stores complete preparation context;
- workflow guides the user through menu, shopping, equipment, and exports;
- completed workflow is usable in Russian on desktop and mobile layouts.