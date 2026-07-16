# Meal Generation Rules Specification

Status:

Accepted

## Purpose

This document describes business rules for automatic hiking menu generation.

The generator creates meal structure, not just a list of dishes.

Structure:

```text
Trip
 |
Day
 |
MealSlot
 |
MealSlotDish
 |
Dish
 |
Recipe
 |
Product
```

MealSlot is the primary persisted meal-composition model. MealPlanItem remains a legacy compatibility view.

---

# Persisted candidate classification

Automatic generation may use only persisted Dish metadata.

Each candidate is evaluated by two dimensions:

1. meal role;
2. compatible meal type for that role assignment.

Supported roles:

- `main`;
- `addition`;
- `drink`;
- `snack`.

Supported meal types:

- `breakfast`;
- `snack`;
- `lunch`;
- `dinner`.

A Dish may have multiple roles. Each `(dish, role)` assignment stores:

- its own `is_repeatable` flag;
- one or more allowed meal types.

Classification belongs to Dish, not Recipe or MealSlotDish.

The generator must not infer classification from:

- the Dish name;
- Recipe name or ingredients;
- Product categories;
- historical MealSlot placement.

Unclassified Dishes remain available for manual selection but are excluded from automatic generation.

A Dish whose selected Recipe is archived is excluded from automatic generation.

---

# Required generated composition

The current required automatic composition is intentionally minimal.

## Breakfast

Required generated component:

- one `main` Dish explicitly compatible with `breakfast`.

Example:

- oatmeal classified as `main → breakfast`.

A Dish classified as `main → lunch,dinner` is not a breakfast candidate.

## Snack

Required generated component:

- one `snack` Dish explicitly compatible with `snack`.

The `snack` role is valid only for the snack MealSlot.

## Lunch

Required generated component:

- one `main` Dish explicitly compatible with `lunch`.

Example:

- borscht classified as `main → lunch,dinner`.

Breakfast-only porridge is not a lunch candidate.

## Dinner

Required generated component:

- one `main` Dish explicitly compatible with `dinner`.

## Optional future components

Recommended main-meal structure also includes:

- an optional compatible `addition`;
- an optional compatible `drink`.

Optional addition/drink generation is a separate implementation slice. Missing optional pools do not block the minimum catalogue-readiness state.

---

# Candidate selection and fallback

For every MealSlot, the generator follows this order:

1. determine the required role for the current meal type;
2. filter Dishes by that persisted role;
3. filter the role assignment by compatibility with the current meal type;
4. exclude Dishes with archived selected Recipes;
5. apply same-day reuse and repeatability rules;
6. select deterministically from the remaining compatible pool.

The generator must never use an incompatible or unclassified Dish as a hidden fallback.

If no required compatible pool exists:

- persist the MealSlot;
- leave its Dish list empty;
- return an explicit warning for the missing role/meal-type pool.

If a compatible non-repeatable pool is exhausted:

- preserve deterministic fallback within that compatible pool;
- return the insufficient-catalogue warning;
- never widen the pool to incompatible Dishes.

If a selected `(dish, role)` assignment has `is_repeatable=true`, same-day reuse is permitted for that role without the insufficient-catalogue warning.

---

# Diversity

Implemented baseline:

- prefer a Dish not yet used on the same trip day;
- reset same-day usage context when the next trip day begins;
- deterministic selection and deterministic compatible-pool fallback.

Required later:

- calendar-day three-day diversity for `main` Dishes;
- larger readiness thresholds for realistic multi-day diversity;
- project-level preferences and constraints.

Selection count must not be described as a calendar-day cooldown.

---

# Composition override

An instructor may manually add, replace, or remove Dishes in a MealSlot.

Manual selections are authoritative for the edited plan.

Preserving manual choices during future full regeneration is a separate implementation slice. Automatic generation must not silently reinterpret manual choices as classification metadata.

---

# Project meal boundaries

The project defines:

- trip duration;
- first meal;
- last meal.

The generated schedule must include only MealSlots inside these boundaries, including one-day projects and incomplete first or last days.

---

# Project meal constraints

Future menu generation may apply project-level restrictions such as:

- forbidden products;
- unwanted products;
- preferred dishes;
- special preparation rules.

Restrictions are evaluated through:

```text
Dish
 |
Recipe
 |
RecipeComponent
 |
Product
```

Strict restrictions must not be silently ignored. If they make a required compatible pool empty, generation must return a warning rather than select an invalid Dish.

---

# Generation priority

The intended long-term priority is:

1. forbidden products and strict restrictions;
2. project meal boundaries and day scenarios;
3. instructor manual settings;
4. persisted role and meal-type compatibility;
5. project preferences;
6. menu diversity;
7. cooking simplicity;
8. weight and transportation convenience.

Only rules backed by persisted data may affect automatic selection.

---

# Warnings and persistence

Generation returns warnings immediately with the generated MealPlan response.

Implemented warnings include:

- no Dishes available;
- no compatible required role pool for a meal type;
- compatible catalogue pool exhausted.

Persisting warnings or deterministically reconstructing them on later GET responses remains future work.

---

# Purchasing separation

The generator works with Dishes and persists MealSlotDish relations.

Product calculation is a separate transactional process:

```text
MealSlotDish → Dish → Recipe → RecipeComponent → Product
```

Role-aware generation must preserve existing purchasing recalculation and legacy MealPlanItem compatibility.
