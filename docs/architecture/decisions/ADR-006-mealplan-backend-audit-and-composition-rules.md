# ADR-006 — MealPlan Backend Audit and Composition Rules

Status:

Partially superseded by ADR-013

Date:

2026-07-09

Supersession note:

- ADR-013 replaces sections 2 and 3 with the current persisted `MealSlot` / `MealSlotDish` composition model and approved `Dish` meal-role metadata.
- The hiking meal examples and composition intent in sections 4 and 5 remain valid.

---

# 1. Purpose

This document fixes the current MealPlan backend state and prevents repeated architectural analysis when continuing development in a new chat/session.

---

# 2. Backend Audit Result — Historical

The original audited model described menu assignments through `MealPlanItem`. This persistence description is retained only as historical context and is superseded by ADR-013.

Original model:

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

The current primary composition model is `MealPlan -> MealPlanDay -> MealSlot -> MealSlotDish -> Dish`.

---

# 3. MealPlanItem Rule — Legacy Compatibility

`MealPlanItem` remains a legacy compatibility path. It is no longer the primary unit of meal composition and must not receive new role metadata or new generation behavior.

Current assignments are persisted through multiple `MealSlotDish` rows in one `MealSlot`.

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

TH-0061.5 — Meal Composition Rules Engine.

The next implementation phase follows ADR-013:

1. add the persisted `dish_meal_roles` model and migration;
2. expose role API contracts;
3. classify the active catalogue explicitly;
4. implement role-aware composition and calendar-day diversity.