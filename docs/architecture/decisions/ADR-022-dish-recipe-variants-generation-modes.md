# ADR-022 — Dish Recipe Variants and Generation Modes

Status: Accepted

Date: 2026-07-18

## Context

A Dish currently points to exactly one Recipe. That makes Recipe ownership and publication usable in the catalogue, but a project cannot select between a club standard and the current instructor's personal variant. Re-reading the mutable Dish default during shopping or equipment recalculation would also change historical project results after a catalogue edit.

## Decision

### Dish catalogue

Dish keeps `recipe_id` as one required default Recipe and gains a complete many-to-many variant set.

- the default must be an active published CLUB Recipe;
- the default must be present in the variant set;
- additional variants may be active published CLUB Recipes or active PERSONAL Recipes visible to the current actor;
- unrelated PERSONAL Recipes are neither accepted by writes nor projected in responses;
- replacing the variant set is atomic;
- removing a variant does not rewrite historical meal assignments.

Keeping the explicit CLUB default provides a stable shared fallback and preserves compatibility for catalogue consumers that have not yet become variant-aware.

### Project generation mode

Project owns one mode:

- `club_only` — eligible published CLUB variants only;
- `club_and_personal` — published CLUB variants first, then active PERSONAL variants owned by the current actor;
- `personal_preferred` — active PERSONAL variants owned by the current actor first, then published CLUB fallback.

Within each group, the Dish default is first when eligible and remaining variants are ordered deterministically. Repeated generated occurrences rotate through the ordered eligible variants. A mode never exposes another user's personal Recipe.

### Assignment snapshot

MealSlotDish and compatibility MealPlanItem store the selected `recipe_id`.

- generation writes the selected Recipe together with the Dish occurrence;
- manually preserved slots retain their stored Recipe;
- manual add and replace use the same Project mode selector;
- purchasing and equipment read the stored assignment Recipe;
- later changes to Dish variants or default do not alter an existing project until regeneration or an explicit manual replacement.

### Migration

Migration `h10019`:

1. creates the Dish-to-Recipe variant table;
2. copies every existing `dishes.recipe_id` into it;
3. adds Project mode with `club_only` default;
4. adds assignment Recipe columns;
5. backfills them from each Dish default;
6. makes assignment Recipe non-null and adds foreign keys/indexes.

## Consequences

- the shared catalogue always has a safe CLUB fallback;
- personal variants affect only the current actor's project generation;
- project calculations are reproducible from persisted assignments;
- the existing Dish default remains a compatibility boundary rather than the source of historical calculations;
- per-meal manual Recipe switching, preference weights, and actor-aware audit remain separate future work.
