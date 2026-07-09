# Meal Generation Rules Specification

Status:

Accepted

## Purpose

This document describes business rules for automatic hiking menu generation.

The generator creates meal structure, not just a list of dishes.

Structure:

```
Trip
 |
 Day
 |
 Meal
 |
 Meal Components
 |
 Dish
 |
 Recipe
 |
 Product
```

---

# Meal composition rules

## Breakfast

Structure:

- main dish (required);
- snacks/additional food (optional);
- drinks (required).

Example:

- porridge;
- sandwiches;
- tea and coffee.

---

## Lunch

Structure:

- main dish (required);
- snacks/additional food;
- drinks.

Example:

- borscht;
- sandwiches;
- compote.

---

## Snack

Purpose:

Energy support between main meals.

Priority:

1. fruits;
2. dried fruits;
3. sweets;
4. cookies;
5. energy bars;
6. sandwiches (rarely).

Example:

- apple.

---

## Dinner

Structure:

- main dish (required);
- salad/additional food;
- drinks.

Example:

- merchant-style buckwheat;
- vitamin salad;
- tea and coffee.

---

# Example day

Breakfast:

- porridge;
- sandwiches;
- tea and coffee.

Lunch:

- borscht;
- sandwiches;
- compote.

Snack:

- apple.

Dinner:

- merchant-style buckwheat;
- vitamin salad;
- tea and coffee.

---

# Dish selection priority

Order of priorities:

1. Instructor favorite dishes.
2. Season compatibility.
3. Product availability.
4. Menu diversity.
5. Cooking simplicity.
6. Weight and transportation convenience.

---

# Generation limitations

If the database does not contain enough dishes:

- reuse available dishes;
- generate warning;
- preserve maximum possible diversity.

---

# Domain rule

The generator works with dishes.

Product calculation is a separate process:

Dish -> Recipe -> Product.
