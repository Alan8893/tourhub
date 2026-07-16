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
- editable required, purchased, and remaining quantities through PR #70;
- package size, count, total quantity, and surplus review through PR #71;
- optional purchasing contact through merged PR #72;
- transactional purchasing recalculation foundations.

## Current implementation slice

### Draft PR #73 — equipment requirements and aggregation

- persist recipe equipment requirements through Alembic `h10005`;
- provide validated add, update, delete, and read-only archived-recipe API behavior;
- generate and persist one EquipmentList for the project;
- sum identical equipment required by recipes in one meal occurrence;
- use the maximum simultaneous quantity across all meal occurrences;
- preserve stable equipment identity and safely replace generated rows;
- expose `equipment_list_id` from project preparation;
- provide Russian recipe controls and a project equipment review;
- verify backend behavior, frontend state, production build, exact GET, screenshot, and 360 px no-overflow.

The functional PR head passed exact-head Quality #331 before documentation synchronization.

This slice does not add project-level manual overrides or participant distribution.

## Next slices

1. Add manual equipment rows, removals, and quantity overrides.
2. Preserve manual overrides while recalculating generated quantities.
3. Refresh equipment after participant, menu, and recipe changes.
4. Complete final Russian PDF/Excel and release acceptance.

## Related decisions

- Project is the preparation aggregate root.
- Recipe owns equipment requirements used during one simultaneous preparation.
- EquipmentList is a persisted project preparation document.
- Identical equipment is summed within one meal occurrence.
- The project requirement is the maximum across meal occurrences, not a trip-wide sum.
- Manual project overrides remain a separate authoritative layer.
- Multi-user access remains deferred until single-user acceptance.

## Acceptance criteria

- recipe equipment requirements persist and can be maintained in Russian;
- preparation creates a persisted project equipment list;
- aggregation follows the maximum simultaneous rule;
- repeated preparation refreshes one list without duplicate rows;
- the workflow is usable on desktop and mobile layouts;
- all backend, frontend, browser, migration, and PostgreSQL quality gates pass.
