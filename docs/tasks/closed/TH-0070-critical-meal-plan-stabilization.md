# TH-0070 — Critical Meal Plan Stabilization

Status: DONE

Priority: P0

## Goal

Repair critical API, frontend, validation, and menu-policy regressions identified by the 2026-07-15 technical audit before new feature development resumes.

## Delivered

- exposed real MealSlotDish identifiers in the MealPlan API;
- used MealSlotDish identifiers for frontend replace/remove operations;
- consumed the backend `/dishes` response envelope correctly;
- restored domain meal order and Russian selector text;
- enforced meal-boundary validation in Backend;
- rejected MealSlot assignment of dishes with archived recipes;
- returned generator warnings from project generation;
- preferred MealSlot data over legacy MealPlanItem data in API mapping;
- removed unsupported standalone meal-plan placeholders;
- removed the invalid selection-based pseudo three-day cooldown;
- added regression tests and menu-engine Ruff/mypy coverage;
- synchronized canonical documentation.

## Non-goals preserved

- no new meal roles;
- no role migration;
- no three-day diversity implementation;
- no equipment domain;
- no access or user roles;
- no architecture or stack change.

## Verification

PR #54 was squash-merged to `main` as commit `c83325320a9c6ac4e1d0419be1135f6c30adb6c2`.

Quality run #153 passed:

- backend tests: 160 passed;
- selected Ruff and strict mypy: passed;
- Alembic single-head validation: passed;
- frontend tests, audit, and production build: passed;
- PostgreSQL backup/restore smoke test: passed.
