# TourHub Current Domain Model

Status: Active

Last updated: 2026-07-15

## Purpose

This document describes the implemented domain baseline. `PRODUCT_SPEC.md` describes approved target scope. Deferred capabilities are not current implementation.

## Club and access

One installation represents one tourist club. Multi-tenant support is prohibited.

The current phase is local and single-user. Invitations, roles, permissions, recipe ownership, publication, moderation, and audit logging are deferred.

## Project

Project is the preparation root for one trip. It stores name, participant count, duration, optional start date, first meal, last meal, status, and preparation results.

`/projects` lists projects. `/projects/{id}` opens one project workspace.

Project creation validates supported meal types and one-day meal ordering in Backend. Participant-count changes preserve selected dishes and recalculate persisted purchasing data transactionally.

## Meal plan

MealPlan contains MealPlanDay records. MealSlot represents one meal occurrence. MealSlotDish is the persisted membership of one Dish in a MealSlot and has its own identifier and order.

The API exposes MealSlotDish identifiers so add, replace, and remove operations address the persisted membership rather than the Dish catalogue record.

Implemented generation behavior:

- first/last meal boundaries;
- one-day trip ranges;
- domain order `breakfast`, `snack`, `lunch`, `dinner`;
- deterministic same-day uniqueness while unused catalogue dishes remain;
- deterministic repetition with a warning after catalogue exhaustion.

Meal-role composition, repeatable-role exceptions, preferences, and calendar-day three-day main-dish diversity remain incomplete. `MealDishRole` is not persisted. The removed selection-based cooldown must not be described as a three-day rule.

Legacy MealPlanItem remains a compatibility path. API mapping uses MealSlot data when it exists and falls back to legacy items only when a day has no MealSlots.

## Dish and recipe

Dish and Recipe are separate entities.

Current persistence stores exactly one selected `recipe_id` on each Dish. Users can create and rename dishes and replace the assigned active recipe. A recipe archived after assignment remains visible historically but cannot be newly assigned to a Dish or MealSlot.

Dish recipe replacement recalculates affected persisted purchasing projections in the same transaction.

Multiple Recipe variants per Dish, CLUB/PERSONAL ownership, publication, and moderation are future work.

Recipe supports components, practical quantity modes, notes, and archive state. Preparation technology, equipment, dietary metadata, season metadata, and richer categories remain incomplete.

## Product and import

Product is independent of recipes. Practical calculation modes include per-person, fixed-group, and package-per-people.

Products, recipes, components, and notes can be loaded through CSV preview and apply operations. Invalid input does not create partial catalogue data.

Product update and deletion are not implemented. The approved alcohol prohibition rule still requires centralized backend enforcement for API and import paths.

## Shopping and packaging

Products are aggregated across RecipeComponents and legacy ingredients. Package rounding foundations exist.

Recalculation triggers include participant-count changes, MealSlot edits, and Dish recipe replacement. Checklist state is preserved for products that remain after refresh. MealSlot mutations and their purchasing refresh share one commit/rollback boundary.

Complete remainder presentation and responsible-person workflow remain incomplete.

## Equipment

Equipment persistence is not implemented. Target behavior is recipe-originated requirements, maximum simultaneous aggregation, and manual overrides.

## Documents

PDF, Excel, and package export foundations exist. Final Russian templates, complete workbook contents, and club branding remain incomplete.

## Future domains

- participant profiles;
- routes and GPX;
- logistics and load distribution;
- warehouse balances;
- procurement prices and aggregator integration.

Multi-tenant support remains prohibited.
