# TH-0065 — Meal Plan Editor UX

Status: active
Priority: P2
Type: frontend / UX

## Problem

The current MealSlot editor is functionally usable but difficult to scan and operate:

- controls are repeated for every dish and consume too much vertical space;
- action labels and select placeholders are partly in English;
- replace, remove, and add actions have weak visual hierarchy;
- meal types are ordered alphabetically instead of by the trip meal sequence;
- long dish names make rows uneven;
- the narrow two-column workspace leaves the menu editor cramped;
- there is no compact summary or collapse behavior for completed days;
- destructive actions do not have an explicit confirmation or undo affordance.

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

## Acceptance criteria

1. An instructor can identify day, meal, and dishes without reading technical controls.
2. Replacing or removing a dish requires no more than two deliberate actions.
3. No English user-facing strings remain in the editor.
4. The editor remains usable at 360 px width.
5. MealSlot mutations continue to trigger purchasing recalculation.
6. Frontend tests cover add, replace, remove, mutation error, and responsive rendering.

## Notes

This is not a release blocker for the current stabilization cycle. It must be completed before the final MVP UI acceptance pass.
