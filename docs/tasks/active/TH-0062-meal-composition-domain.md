# TH-0062 — Meal Composition Domain

Status: ACTIVE

## Goal

Improve MealPlan domain to support realistic hiking meals.

## Problem

A meal is not equal to one dish.

Examples:

Breakfast:
- porridge
- sandwiches
- tea

Lunch:
- soup
- sandwiches
- drink

## Target Model

MealSlot
 |
 Dish[]

## Requirements

- support multiple dishes per meal;
- keep shopping calculation compatible;
- allow instructor editing;
- support dish replacement.

## Constraints

- do not break RecipeComponent;
- do not rewrite MealPlan;
- use evolutionary migration.

## Definition of Done

- domain model updated;
- tests added;
- documentation updated;
- roadmap updated.
