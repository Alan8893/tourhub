# ADR-008 — Meal Composition Overrides and Project Constraints

Status:

Accepted

Date:

2026-07-09

---

# Context

Real hiking scenarios require flexibility in meal planning.

Standard meal templates are recommendations, not strict rules.

Examples:

- the last day may require a fast meal before departure;
- a one-day trip may consist only of a snack;
- an instructor may need to manually change meal composition.

---

# Decision

Meal generation supports three levels:

## 1. Automatic generation

System generates meals using standard composition rules.

## 2. Semi-automatic generation

Instructor defines allowed meal components and the system selects dishes.

## 3. Manual selection

Instructor chooses dishes directly.

---

# Composition Override

Default templates:

Breakfast:

- main dish;
- additional food;
- drinks.

Lunch:

- main dish;
- additional food;
- drinks.

Snack:

- fruits;
- sweets;
- rarely sandwiches.

Dinner:

- main dish;
- salad/additional food;
- drinks.

Templates can be overridden for a specific project or meal.

---

# Project Meal Constraints

Nutrition generation uses project-level constraints.

Examples:

- forbidden products;
- unwanted products;
- special preparation rules.

The system does not model participants at this stage.

Future participant modules may provide constraints, but current scope uses project constraints only.

---

# Constraint Priority

Order:

1. Forbidden products and strict restrictions.
2. Day scenario constraints.
3. Manual instructor settings.
4. Project preferences.
5. Favorite dishes.
6. Seasonality.
7. Availability.
8. Diversity.
9. Cooking simplicity.
10. Weight optimization.

---

# Validation

Before generation:

- verify that valid dishes exist;
- verify restrictions can be satisfied;
- return warnings when generation quality is limited.

The system must not silently generate invalid menus.

---

# Scope

No Participant domain is introduced.

No participant profiles or medical records are created.

Current solution is internal ERP focused on project preparation.
