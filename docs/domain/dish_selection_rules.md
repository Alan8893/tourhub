# Dish Selection Priority Rules

Status:

Accepted

## Purpose

Defines how the menu generator chooses dishes.

## Priority order

The generator uses the following priorities:

```
1. Instructor favorite dishes
        |
2. Season compatibility
        |
3. Product availability
        |
4. Menu diversity
        |
5. Cooking simplicity
        |
6. Weight and transportation convenience
```

---

# Future Dish metadata

The following attributes may be introduced later:

```
Dish
 |
 + meal_types
 + composition_type
 + season
 + cooking_complexity
 + preparation_time
 + weight_factor
```

These fields are future extensions and are not added to the database yet.

---

# Architectural rule

Do not create additional database entities until current domain model becomes insufficient.

Current MealPlanItem model already supports multiple dishes per meal.
