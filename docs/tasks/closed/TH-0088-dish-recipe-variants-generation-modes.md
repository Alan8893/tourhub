# TH-0088 — Dish Recipe Variants and Generation Modes

Status: DONE

Completed: 2026-07-18

## Goal

Allow one Dish to own multiple ordered Recipe variants and make each Project choose Recipes according to the approved club/personal generation mode while preserving the exact selected Recipe on every meal-plan assignment.

## Delivered

### Persistence

- added ordered `dish_recipe_variants` with `(dish_id, recipe_id)` identity and non-negative `position`;
- retained `dishes.recipe_id` as the required published CLUB default;
- migrated every existing Dish default to position zero;
- added Project `recipe_generation_mode`: `club_only`, `club_and_personal`, or `personal_preferred`;
- added non-null selected `recipe_id` to MealSlotDish and compatibility MealPlanItem;
- backfilled existing meal assignments from the current Dish default;
- advanced Alembic from `h10018` to `h10019` with one head.

### Backend

- Dish create/update atomically replaces the complete ordered variant set;
- the default must be an active published CLUB Recipe and be included in the set;
- additional variants may be published CLUB or current-actor-visible PERSONAL Recipes;
- unrelated PERSONAL variants remain private and are rejected by writes;
- Project mode determines CLUB/PERSONAL group priority;
- default CLUB remains the shared fallback and variant rotation is deterministic;
- manually edited slots preserve exact selected Recipes during regeneration;
- manual add/replace uses the same Project mode policy;
- shopping and equipment calculations use persisted assignment Recipes;
- catalogue default/variant changes do not reinterpret historical assignments.

### Frontend

- Dish catalogue edits one CLUB default plus additional ordered variants;
- variant cards show CLUB/PERSONAL scope, owner, default, and archive state;
- Project creation and workspace expose the generation mode with explanations;
- Project header shows the current mode;
- meal-plan assignments display their stored Recipe;
- compatibility normalization keeps rolling-update browser fixtures safe;
- responsive catalogue and guided workflow behavior are preserved.

### Validation

- focused tests cover all three modes, unrelated PERSONAL filtering, persisted order, deterministic rotation, manual preservation, assignment shopping snapshots, and migration compatibility;
- Backend, Frontend, browser, guided release, PostgreSQL backup/restore, operator docs, document quality, and clean Docker release runtime are exact-head gates;
- ADR-022 and current status/domain/architecture/roadmap/debt/operator documentation are synchronized.

## Out of scope

- preference weights beyond the three approved modes;
- per-meal manual Recipe switching without changing Dish;
- central alcohol policy;
- actor-aware audit and immutable moderation history;
- project ACLs, multi-tenancy, or live collaboration.
