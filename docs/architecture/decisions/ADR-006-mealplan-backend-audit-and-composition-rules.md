# ADR-006 — MealPlan Backend Audit and Composition Rules

Status:

Accepted

Date:

2026-07-09

---

# 1. Purpose

This document fixes the current MealPlan backend state and prevents repeated architectural analysis when continuing development in a new chat/session.

---

# 2. Backend Audit Result

## Existing domain model

MealPlan already has the required persistence structure:

Project
 |
 MealPlan
 |
 MealPlanDay
 |
 MealPlanItem[]
 |
 Dish
 |
 Recipe
 |
 Product

A new MealSlot table or MealComposition table is NOT required.

---

# 3. MealPlanItem Rule

MealPlanItem is the existing unit of a dish assignment.

One meal is represented by multiple MealPlanItem records with the same:

- day_number;
- meal_type.

Example:

Day 1

Breakfast:

- MealPlanItem -> Porridge
- MealPlanItem -> Sandwiches
- MealPlanItem -> Tea

---

# 4. Meal Composition Rules

The generator must build meals using real hiking practice.

## Breakfast

Composition:

- main dish;
- snacks/additional food;
- drinks.

Example:

Breakfast:

- porridge;
- sandwiches;
- tea and coffee.

---

## Lunch

Composition:

- main dish;
- snacks/additional food;
- drinks.

Example:

Lunch:

- borscht;
- sandwiches;
- compote.

---

## Snack

Composition:

Usually:

- fruits;
- sweets.

Rarely:

- sandwiches.

Example:

Snack:

- apple.

---

## Dinner

Composition:

- main dish;
- salad or additional food;
- drinks.

Example:

Dinner:

- merchant-style buckwheat;
- vitamin salad;
- tea and coffee.

---

# 5. Example Day

Day 1:

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

# 6. Development Rule

Before implementing changes, the AI assistant must first read:

- PROJECT_CONTEXT.md;
- ARCHITECTURE.md;
- DOMAIN.md;
- DEVELOPMENT_RULES.md;
- relevant ADR documents;
- active task documentation.

Only after documentation analysis may code changes be proposed or implemented.

---

# 7. Future Work

Next implementation phase:

TH-0061.5 — Meal Composition Rules Engine.

Goal:

Convert generic dish generation into rule-based meal generation.
