# TH-0061 — User Project Preparation Wizard

Status: IN PROGRESS

Last updated: 2026-07-16

## Goal

Create a complete guided Russian scenario for preparing a hiking project from creation through final outputs.

## Completed

- project creation, catalogue, workspace, participants, duration, and meal boundaries;
- role-aware menu generation, manual editing, diversity, and warnings;
- purchasing review, packaging, surplus, and purchasing contact through PRs #70–#72;
- recipe equipment requirements and maximum simultaneous aggregation through PR #73;
- project equipment additions, removals, quantity overrides, and recalculation preservation through merged PR #74.

## Current slice — draft PR #75

- refresh every prepared EquipmentList using a recipe after requirement POST, PUT, or DELETE;
- flush the requirement mutation before recalculation;
- commit the source mutation and all derived refreshes in one transaction;
- preserve overrides, removal decisions, and manual rows;
- leave projects without a prepared EquipmentList unchanged;
- cover two prepared projects, one unprepared project, all CRUD operations, and rollback on refresh failure;
- enforce the recalculation service in stabilized Ruff and strict mypy gates.

Functional head `4e6f6a09e11435199e5c7fcb59c444f642d25388` passed Quality #353 before documentation synchronization.

## Next

1. Include equipment in final Russian PDF and Excel outputs.
2. Add club branding and complete guided-preparation acceptance.
3. Complete installation, upgrade, Docker build, and release validation.

## Decisions

- Project is the preparation aggregate root.
- Recipe owns simultaneous equipment requirements.
- EquipmentList is a persisted project preparation document.
- Project quantity is the maximum across meal occurrences.
- Calculated quantity remains separate from the final user-controlled quantity.
- Manual additions, removals, and overrides are authoritative during recalculation.
- Direct recipe requirement changes update prepared lists transactionally.

## Acceptance criteria

- equipment requirements persist and aggregate correctly;
- project equipment remains editable in Russian;
- user decisions survive every recalculation path;
- direct recipe-equipment changes refresh all prepared affected projects;
- unprepared projects receive no implicit derived list;
- all backend, frontend, browser, migration, and PostgreSQL gates pass.
