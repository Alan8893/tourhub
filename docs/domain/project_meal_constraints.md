# Project Meal Constraints

Status:

Accepted

## Purpose

Defines restrictions and preferences applied to menu generation for a specific hiking project.

The current product does not contain participant entities.

Constraints belong to the Project context.

---

# Constraint Types

## Forbidden

Strict restrictions.

Examples:

- allergy-related products;
- ingredients that must never appear.

Generator must exclude matching dishes.

---

## Avoid

Soft restrictions.

Examples:

- disliked products;
- products the group prefers not to use.

Generator should avoid when possible.

---

## Preferred

Positive preferences.

Examples:

- favorite dishes;
- preferred menu options.

---

# Ingredient Validation

Restrictions apply through the full chain:

Dish
 |
Recipe
 |
Ingredients
 |
Products

A dish is invalid if any forbidden ingredient is included.

---

# Failure Handling

If constraints make generation impossible:

- do not silently ignore restrictions;
- return warnings;
- explain that available dishes are insufficient.

---

# Future Extension

If participant management is introduced in the future:

Participant data may become a source of project constraints.

The current domain remains project-based.
