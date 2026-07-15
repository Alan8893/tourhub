# TH-0065 — Meal Plan Editor UX

Status: IN PROGRESS
Priority: P2
Type: frontend / UX

## Problem

The original MealSlot editor was functionally usable but difficult to scan and operate:

- controls were repeated for every dish and consumed too much vertical space;
- replace, remove, and add actions had weak visual hierarchy;
- long dish names made rows uneven;
- the narrow two-column workspace left the menu editor cramped;
- there was no compact summary or collapse behavior for completed days;
- destructive actions did not have an explicit confirmation or undo affordance.

The stabilization PR #54 already corrected the MealSlot identifiers, dish-list API envelope, meal ordering, and remaining English selector text.

## Target UX

- fully Russian labels and placeholders;
- stable meal ordering: breakfast, snack, lunch, dinner, constrained by first/last meal;
- one compact row per dish with clear replace and remove actions;
- add-dish action separated from existing dishes;
- responsive full-width menu editor when editing is the primary task;
- collapsible day sections with dish counts;
- loading, success, and error feedback for each mutation;
- accessible controls with tooltips and clear destructive styling;
- usable desktop, tablet, and mobile layouts.

## Current implementation slice

Branch `agent/meal-plan-editor-ux` adds:

- progressive disclosure for replacement and addition selectors;
- explicit two-step removal confirmation;
- Russian success and error feedback;
- compact outlined dish rows with long-name wrapping;
- responsive column/row action layout;
- collapsible days with dish counts and only the first day expanded by default;
- a full-width Meal Plan workspace;
- state-level tests for add, replace, remove, errors, feedback, Russian plurals, meal ordering, day summaries, collapse defaults, and responsive policy;
- synchronized roadmap, status, technical debt, and task documentation after TH-0070.

## Acceptance criteria

1. An instructor can identify day, meal, and dishes without reading technical controls.
2. Replacing or removing a dish requires no more than two deliberate actions.
3. No English user-facing strings remain in the editor.
4. The editor remains usable at 360 px width.
5. MealSlot mutations continue to trigger purchasing recalculation.
6. Frontend tests cover add, replace, remove, mutation error, and responsive behavior.

## Remaining before DONE

- successful Quality workflow for the current implementation slice;
- browser-level React/API integration tests for add, replace, remove, and mutation errors;
- explicit browser verification at 360 px, tablet, and desktop widths;
- final Product Owner UX acceptance.

## Notes

This task is not a backend business-rules task. MealSlot purchasing recalculation and validation remain owned by FastAPI.
