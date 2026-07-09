# ADR-011 — Recipe Components and Recipe Variants

Status:

Accepted

Date:

2026-07-09

---

# Context

TourHub needs a realistic hiking food model.

Instructors do not work with professional cooking recipes. They work with practical hiking preparation rules:

Example:

```
Antonsky salad:

beans: 1 can / 4 people
corn: 1 can / 4 people
peas: 1 can / 4 people
crackers: 1 pack / 2 people
```

The current domain already contains Dish, Recipe and Ingredient concepts, but they need to support real hiking scenarios.

---

# Decision

## Dish is not Recipe

A Dish represents the meal concept.

Example:

```
Dish:
Borscht
```

A Dish can have multiple Recipes.

```
Borscht
 |
 + Standard recipe
 + Instructor recipe with beans
```

---

# Recipe is a variant

A Recipe represents a concrete way to prepare a Dish.

A new Recipe should be created when preparation rules differ significantly.

Do not create duplicate Dishes for small variations.

---

# Recipe ownership

Initial scopes:

## System Recipe

Default recipe available in the system.

## Instructor Recipe

Personal recipe created by an instructor.

The system has one club instance.

No tenant, organization or club separation is introduced.

---

# Recipe Components

Recipe consists of components.

Components have roles.

## Base Component

Mandatory part of the dish.

Example:

```
porridge:
oats
water
salt
```

---

## Cooking Component

Technology-related ingredients.

Example:

```
salt
spices
oil
```

---

## Optional Component

Can be added or removed.

Example:

```
nuts
dried fruits
honey
```

---

## Serving Add-on

Added during serving.

Example:

```
jam
nuts
condensed milk
```

---

# Restrictions

Product restrictions are evaluated by component type.

Rules:

- forbidden Base component => recipe unavailable;
- forbidden Cooking component => recipe unavailable;
- forbidden Optional component => component excluded;
- forbidden Serving Add-on => not provided.

---

# Quantity Rules

Recipe components support hiking-oriented quantities.

The model must support:

```
amount
unit
people_count
```

Examples:

```
1 can / 4 people
1 pack / 2 people
120 g / person
```

---

# Compatibility

The decision preserves existing flow:

```
Dish
 ↓
Recipe
 ↓
Recipe Components
 ↓
Products
 ↓
Shopping
```

MealPlan remains independent from product calculation.

---

# Consequences

Positive:

- instructors can create personal variants;
- database avoids duplicate dishes;
- shopping calculation becomes more accurate;
- allergies and exclusions become manageable.

Negative:

- recipe model becomes richer;
- migration from current Ingredient model is required.

---

# Future Extensions

Possible future additions:

- recipe versioning;
- approval workflow;
- recipe sharing between instructors.
