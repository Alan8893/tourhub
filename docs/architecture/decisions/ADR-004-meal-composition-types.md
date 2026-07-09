# ADR-004 — Meal Composition Types

Status:

Accepted

## Problem

A hiking meal consists of multiple dishes.

Example:

Breakfast:
- porridge
- sandwiches
- tea

## Decision

MealPlanItem remains a dish assignment inside a meal slot.

Meal composition is represented by multiple MealPlanItem records sharing:

- same day;
- same meal_type.

## Future Extension

A separate composition category may be introduced:

- main dish;
- side dish;
- drink;
- snack.

This is deferred until menu generation requires it.
