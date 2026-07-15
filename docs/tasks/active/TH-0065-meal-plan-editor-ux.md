# TH-0065 — Meal Plan Editor UX

Status: READY FOR REVIEW
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

The stabilization PR #54 corrected the MealSlot identifiers, dish-list API envelope, meal ordering, and remaining English selector text.

## Delivered UX

- fully Russian labels and placeholders;
- stable meal ordering: breakfast, snack, lunch, dinner, constrained by first/last meal;
- compact rows with clear replace and remove actions;
- progressive disclosure for replacement and addition selectors;
- explicit two-step removal confirmation;
- loading, success, and error feedback for mutations;
- accessible controls with tooltips and destructive styling;
- collapsible day sections with dish counts;
- full-width workspace for the primary menu-editing task;
- responsive desktop, tablet, and 360 px mobile layouts.

## Automated acceptance

PR #57 adds a dependency-free browser acceptance runner using Chrome DevTools Protocol, Vite, and an in-process mock API.

Quality run #164 verifies:

- add, replace, and remove requests through the real React hooks and Axios client;
- explicit removal confirmation;
- Russian success and injected mutation-error feedback;
- no horizontal overflow at 1280, 768, and 360 px;
- captured desktop, tablet, and mobile screenshots;
- existing frontend Node tests, dependency audit, and production build;
- backend quality gates and PostgreSQL backup/restore.

## Acceptance criteria

1. An instructor can identify day, meal, and dishes without reading technical controls.
2. Replacing or removing a dish requires no more than two deliberate actions.
3. No English user-facing strings remain in the editor.
4. The editor remains usable at 360 px width.
5. MealSlot mutations continue to trigger purchasing recalculation.
6. Frontend tests cover add, replace, remove, mutation error, and responsive behavior.

All automated acceptance criteria are satisfied on PR #57.

## Remaining before DONE

- Product Owner visual acceptance of the desktop, tablet, and mobile screenshots;
- squash merge of PR #57 with unchanged successful Quality checks;
- move this task to `closed/` after merge verification.

## Notes

This task is not a backend business-rules task. MealSlot purchasing recalculation and validation remain owned by FastAPI.
