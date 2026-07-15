# TourHub Current Domain Model

Status: Active

Last updated: 2026-07-15

## Purpose

This document describes the implemented domain baseline. `PRODUCT_SPEC.md` describes approved target scope. Deferred capabilities are not current implementation.

## Club and access

One installation represents one tourist club. Multi-tenant support is prohibited.

The current phase is local and single-user. Invitations, roles, permissions, recipe ownership, publication, and moderation are deferred.

## Project

Project is the preparation root for one trip. It stores name, participant count, duration, optional start date, first and last meal, status, and preparation results.

`/projects` lists all projects. `/projects/{id}` opens one project workspace.

Participant-count changes preserve selected dishes and recalculate persisted purchasing data transactionally.

## Meal plan

MealPlan contains MealPlanDay records. MealSlot represents one meal occurrence and contains one or more dishes.

Users can add, remove, and replace dishes. These operations refresh affected purchase lists and checklists transactionally.

Meal composition, three-day diversity, same-day uniqueness, preferences, and insufficient-catalogue warnings remain incomplete.

## Dish and recipe

Dish and Recipe are separate entities.

Current persistence stores exactly one selected `recipe_id` on each Dish. Users can create and rename dishes and replace the assigned active recipe. A recipe archived after assignment remains visible historically but cannot be newly assigned.

Dish recipe replacement recalculates every affected persisted purchasing projection in the same transaction.

Multiple Recipe variants per Dish, CLUB/PERSONAL ownership, publication, and moderation are approved future work and are not yet persisted.

Recipe currently supports components, practical quantity modes, notes, and archive state. Preparation technology, equipment, dietary metadata, season metadata, and richer categories remain incomplete.

## Product and import

Product is independent of recipes. Practical calculation modes include per-person, fixed-group, and package-per-people.

Products, recipes, components, and notes can be loaded through CSV preview and apply operations. Invalid input does not create partial catalogue data.

The approved alcohol prohibition rule still requires centralized backend enforcement for API and import paths.

## Shopping and packaging

Products are aggregated across recipe components and legacy ingredients. Package rounding foundations exist.

Recalculation triggers currently include participant-count changes, MealSlot edits, and Dish recipe replacement. Checklist state is preserved for products that remain after refresh.

Complete remainder presentation and responsible-person workflow remain incomplete.

## Equipment

Equipment persistence is not implemented. Target behavior is recipe-originated requirements, maximum simultaneous aggregation, and manual overrides.

## Documents

PDF, Excel, and package export foundations exist. Final Russian templates, complete workbook contents, and club branding remain incomplete.

## Audit

Audit logging is deferred until identity and roles exist.

## Future domains

- participant profiles;
- routes and GPX;
- logistics and load distribution;
- warehouse balances;
- procurement prices and aggregator integration.

Multi-tenant support remains prohibited.