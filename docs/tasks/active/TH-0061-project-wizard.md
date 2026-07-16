# TH-0061 — User Project Preparation Wizard

Status: IN PROGRESS

Last updated: 2026-07-16

## Goal

Create a complete guided Russian scenario for preparing a hiking project from creation through final outputs.

## Completed

- project creation, catalogue, and workspace;
- participant count, duration, and meal boundaries;
- persisted role-aware menu generation and manual editing;
- diversity rules and persisted generation warnings;
- purchase list and checklist persistence;
- editable purchase progress, package review, surplus, and purchasing contact through PRs #70–#72;
- recipe equipment requirements and maximum simultaneous project aggregation through merged PR #73;
- transactional purchasing recalculation foundations.

## Current implementation slice

### Draft PR #74 — project equipment overrides and recalculation

- add Alembic `h10006` fields for calculated baseline, manual rows, and persisted removals;
- keep `required_quantity` as the final user-facing value;
- allow manual equipment additions, quantity overrides, and removals in the project workspace;
- preserve manual additions and overrides during repeated project preparation;
- preserve removal decisions for generated rows while their calculated source still exists;
- convert an overridden generated row to a manual row if its calculated source disappears;
- refresh existing equipment after meal-slot edits, Dish recipe changes, participant changes, and full menu regeneration;
- display calculated, manually added, and overridden state in Russian;
- verify API behavior, strict typing, frontend state, production build, interactive browser CRUD, refetch, screenshot, and 360 px no-overflow.

The functional PR head `cef66b99c4546805cffc0ad0e445e0fe8048e86c` passed Quality #349 before documentation synchronization.

## Next slices

1. Refresh prepared project equipment lists after direct recipe-equipment requirement changes.
2. Include equipment in final Russian PDF and Excel outputs.
3. Complete guided-preparation and release acceptance.

## Related decisions

- Project is the preparation aggregate root.
- Recipe owns equipment requirements for one simultaneous preparation.
- EquipmentList is a persisted project preparation document.
- Identical equipment is summed within one meal occurrence.
- The project requirement is the maximum across meal occurrences, not a trip-wide sum.
- Calculated quantity remains visible separately from the final user-controlled quantity.
- Manual additions, removals, and quantity overrides are authoritative during recalculation.
- Multi-user access remains deferred until single-user acceptance.

## Acceptance criteria

- recipe equipment requirements persist and aggregate correctly;
- the project equipment list can be edited in Russian;
- manual additions, removals, and quantity overrides survive regeneration;
- meal, Dish recipe, participant, and full menu changes refresh the calculated baseline;
- calculated and user-controlled values remain distinguishable;
- the workflow is usable on desktop and mobile layouts;
- all backend, frontend, browser, migration, and PostgreSQL quality gates pass.
