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

Meal templates are recommendations, not strict requirements.

An instructor can override the composition for a specific project or meal.

---

## Breakfast

Recommended structure:

- main dish;
- snacks/additional food;
- drinks.

Example:

- porridge;
- sandwiches;
- tea and coffee.

---

## Lunch

Recommended structure:

- main dish;
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
6. sandwiches rarely.

Example:

- apple.

---

## Dinner

Recommended structure:

- main dish;
- salad/additional food;
- drinks.

Example:

- merchant-style buckwheat;
- vitamin salad;
- tea and coffee.

---

# Composition override

Real hiking scenarios require flexible meal composition.

Examples:

## Last day before departure

A normal lunch may be replaced by a fast meal:

- salad;
- cold food;
- simple snack.

Reason:

The group must leave on time for transport.

## One-day trip

A project may contain only:

- snack;

or another minimal meal configuration chosen by the instructor.

The generator must support reduced meal plans.

---

# Project meal constraints

Menu generation uses project-level restrictions.

Examples:

- forbidden products;
- unwanted products;
- preferred dishes;
- special preparation rules.

Restrictions are applied through:

```
Dish
 |
 Recipe
 |
 Ingredients
 |
 Products
```

A dish containing forbidden ingredients cannot be selected.

---

# Generation priority

The generator follows this order:

1. Forbidden products and strict restrictions.
2. Day scenario constraints.
3. Instructor manual settings.
4. Project preferences.
5. Favorite dishes.
6. Season compatibility.
7. Product availability.
8. Menu diversity.
9. Cooking simplicity.
10. Weight and transportation convenience.

---

# Day context

Day context can affect meal generation.

Examples:

- first day;
- last day;
- incomplete day;
- limited preparation time.

Transport logistics are a separate future domain and are not implemented here.

---

# Generation limitations

If the database does not contain enough dishes:

- reuse available dishes;
- generate warning;
- preserve maximum possible diversity.

If restrictions make generation impossible:

- do not silently ignore restrictions;
- return warnings explaining the problem.

---

# Domain rule

The generator works with dishes.

Product calculation is a separate process:

```
Dish -> Recipe -> Product
```
