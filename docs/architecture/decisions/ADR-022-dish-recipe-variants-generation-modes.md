# ADR-022 — Dish Recipe Variants and Generation Modes

Status: Accepted

Date: 2026-07-18

## Context

A Dish previously pointed to exactly one Recipe. Recipe ownership and publication made club and personal recipes available, but a project could not select between a club standard and the current instructor's personal variant. Re-reading the mutable Dish default during shopping or equipment recalculation would also change historical project results after a catalogue edit.

## Decision

### Dish catalogue

Dish keeps `recipe_id` as one required default Recipe and gains a complete ordered many-to-many variant set.

- the default must be an active published CLUB Recipe;
- the default must be present in the variant set;
- `DishRecipeVariant.position` persists the caller-defined order;
- the `(dish_id, recipe_id)` primary key prevents duplicate variants;
- positions must be non-negative; the application rewrites them sequentially when replacing the set;
- additional variants may be active published CLUB Recipes or active PERSONAL Recipes visible to the current actor;
- unrelated PERSONAL Recipes are neither accepted by writes nor projected in responses;
- replacing the variant set is atomic;
- removing or reordering a variant does not rewrite historical meal assignments.

Keeping the explicit CLUB default provides a stable shared fallback and preserves compatibility for consumers that are not yet variant-aware.

### Project generation mode

Project owns one mode:

- `club_only` — eligible published CLUB variants only;
- `club_and_personal` — published CLUB variants first, then active PERSONAL variants owned by the current actor;
- `personal_preferred` — active PERSONAL variants owned by the current actor first, then published CLUB fallback.

Within the CLUB group, the Dish default is moved to the first position when eligible. All remaining variants preserve their persisted relative order. Repeated generated occurrences rotate deterministically through the ordered eligible variants. A mode never exposes another user's personal Recipe.

Changing the Project mode affects later generation and manual assignments. It does not rewrite existing assignment snapshots.

### Assignment snapshot

MealSlotDish and compatibility MealPlanItem store the selected `recipe_id`.

- generation writes the selected Recipe together with the Dish occurrence;
- manually preserved slots retain their stored Recipe;
- manual add and replace use the same Project mode selector;
- purchasing and equipment read the stored assignment Recipe;
- later changes to Dish variants or default do not alter an existing project until regeneration or explicit manual replacement.

### Migration

Migration `h10019`:

1. creates the ordered Dish-to-Recipe variant table;
2. copies every existing `dishes.recipe_id` into position zero;
3. adds Project mode with `club_only` default;
4. adds assignment Recipe columns;
5. backfills them from each Dish default;
6. makes assignment Recipe non-null and adds foreign keys/indexes.

## Consequences

- the shared catalogue always has a safe CLUB fallback;
- personal variants affect only the current actor's selection context;
- project calculations are reproducible from persisted assignments;
- the existing Dish default remains a compatibility boundary rather than the source of historical calculations;
- the UI can display the stored Recipe without recomputing selection;
- per-meal manual Recipe switching, preference weights, and actor-aware audit remain separate future work.
