# TH-0070 — Critical Meal Plan Stabilization

Status: READY FOR REVIEW

Priority: P0

## Goal

Repair critical API, frontend, validation, and menu-policy regressions identified by the 2026-07-15 technical audit before new feature development resumes.

## Scope

- expose real MealSlotDish identifiers in the MealPlan API;
- use MealSlotDish identifiers for frontend replace/remove operations;
- consume the backend `/dishes` response envelope correctly;
- restore domain meal order and Russian selector text;
- enforce meal-boundary validation in Backend;
- reject MealSlot assignment of dishes with archived recipes;
- return generator warnings from project generation;
- prefer MealSlot data over legacy MealPlanItem data in API mapping;
- remove unsupported standalone meal-plan placeholders;
- remove the invalid selection-based pseudo three-day cooldown;
- add regression tests and menu-engine Ruff/mypy coverage;
- synchronize canonical documentation.

## Non-goals

- no new meal roles;
- no role migration;
- no three-day diversity implementation;
- no equipment domain;
- no access or user roles;
- no architecture or stack change.

## Acceptance criteria

- MealSlot add, replace, and remove use the correct persisted identifiers;
- frontend dish loading matches the backend response;
- invalid project meal boundaries are rejected by FastAPI;
- archived-recipe dishes cannot be newly assigned to MealSlots;
- project generation returns insufficient-catalogue warnings;
- API flat items are not duplicated when MealSlots exist;
- no public fake meal-plan response remains;
- current documentation does not claim three-day diversity exists;
- backend, frontend, Ruff, mypy, Alembic, audit, build, and backup/restore checks pass.

## Delivery

Draft PR: #54.
