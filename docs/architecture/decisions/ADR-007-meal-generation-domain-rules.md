# ADR-007 — Meal Generation Domain Rules

Status:

Accepted

## Context

TourHub menu generation must represent real hiking meal practices.

## Decisions

1. Generator works with dishes, not products.

```
Dish
 |
Recipe
 |
Product
```

2. Product calculation is a separate business process.

3. MealPlanItem remains the atomic stored unit of a dish assignment.

4. One meal is represented by multiple MealPlanItem records sharing:

- day_number;
- meal_type.

5. Meal generation rules are defined by meal type:

- breakfast: main dish + snacks + drinks;
- lunch: main dish + snacks + drinks;
- snack: fruits/sweets, rarely sandwiches;
- dinner: main dish + salad/additional food + drinks.

## Consequence

No MealSlot or MealComposition database entity is introduced at this stage.

Composition is handled by generation rules and existing MealPlanItem records.
