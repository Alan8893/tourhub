# TH-0088 — Dish Recipe Variants and Generation Modes

Status: IN PROGRESS

Last updated: 2026-07-18

## Goal

Allow one Dish to own multiple Recipe variants and make each project choose recipes according to the approved club/personal generation mode while preserving the exact selected Recipe on every meal-plan assignment.

## Scope

### Persistence

- add `dish_recipe_variants` as the many-to-many catalogue relation;
- keep `dishes.recipe_id` as the required published CLUB default for compatibility and deterministic fallback;
- migrate every existing Dish default into its variant set;
- add Project `recipe_generation_mode`: `club_only`, `club_and_personal`, or `personal_preferred`;
- add non-null selected `recipe_id` to MealSlotDish and compatibility MealPlanItem;
- backfill existing meal assignments from the current Dish default;
- advance Alembic from `h10018` to `h10019` with one head.

### Backend

- allow Dish create/update to replace the complete variant set while retaining one CLUB published default;
- allow active CLUB published variants and current-actor-visible active PERSONAL variants;
- hide unrelated PERSONAL variants from Dish responses;
- choose eligible variants per current actor and Project mode;
- `club_only`: only CLUB published variants;
- `club_and_personal`: CLUB variants first, then current actor PERSONAL variants, rotating deterministically across repeated Dish occurrences;
- `personal_preferred`: current actor PERSONAL variants first, then CLUB fallback;
- preserve selected variants during regeneration of manually edited slots;
- use stored assignment Recipe for shopping and equipment calculations;
- manual add/replace selects a variant through the same Project mode policy;
- prevent archive/delete/default replacement paths from silently invalidating persisted historical assignments.

### Frontend

- edit one default recipe plus additional variants on the Dish catalogue;
- show CLUB/PERSONAL variant scope without exposing unrelated personal recipes;
- configure the Project generation mode;
- show the selected Recipe for each meal-plan assignment;
- keep existing responsive catalogue and guided workflow behavior.

## Out of scope

- recipe preference weights beyond the three approved modes;
- per-meal manual Recipe switching without changing Dish;
- project ownership or participant profiles;
- central alcohol policy;
- actor-aware audit;
- multi-tenancy or live collaboration.

## Definition of done

- all existing Dish and meal-plan data migrate without losing the current recipe;
- every active Dish has a published CLUB default included in its variant set;
- automatic and manual meal assignments persist the exact chosen Recipe;
- shopping and equipment use assignment recipes rather than mutable Dish defaults;
- generation modes are deterministic and actor-aware;
- unrelated PERSONAL variants remain private;
- focused Backend and browser acceptance covers modes, fallback, persistence, and responsive UI;
- current domain, architecture, roadmap, status, technical debt, task index, operator docs, and ADR are synchronized;
- exact-head repository quality gates pass.
