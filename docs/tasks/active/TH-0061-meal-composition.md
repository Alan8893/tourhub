# TH-0061.4 — Meal Composition Model

Status:

TECH DEBT

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

Dinner:
- main dish
- salad
- tea

## Required Model

MealSlot
 |
 Dish[]

## Impact

Required for:

- realistic menu generation;
- correct shopping calculation;
- dish replacement;
- instructor editing.

## Priority

High
