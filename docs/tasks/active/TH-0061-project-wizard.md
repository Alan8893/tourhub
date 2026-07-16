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
- transactional purchasing recalculation foundations.

## Current implementation slice

### Draft PR #72 — optional purchasing contact

- add nullable PurchaseList persistence through Alembic `h10004`;
- expose the value in GET and update it through PATCH;
- trim saved text, clear blank values, and enforce a 255-character limit;
- preserve the value when purchase-list items are recalculated;
- provide Russian save/clear controls and feedback;
- verify persistence, refetch, clearing, and 360 px layout through API, unit, service, and browser tests.

This remains free text. User accounts, invitations, role assignment, and notifications are out of scope.

## Next slices

1. Persist and aggregate recipe equipment requirements.
2. Support manual equipment overrides and recalculation.
3. Complete final Russian PDF/Excel and release acceptance.

## Related decisions

- Project is the preparation aggregate root.
- PurchaseList owns package review metadata.
- Purchase progress remains user-controlled during recalculation.
- The purchasing contact remains attached to PurchaseList while item rows are rebuilt.
- Multi-user access remains deferred until single-user acceptance.

## Acceptance criteria

- shopping quantities and packaging are reviewable in Russian;
- the optional purchasing contact persists, can be cleared, and survives recalculation;
- the workflow is usable on desktop and mobile layouts;
- all backend, frontend, browser, migration, and PostgreSQL quality gates pass.
