# TH-0063 — Meal Editing Workflow

Status: ACTIVE

## Goal

Allow instructors to edit generated meal compositions.

## Context

MealSlot now supports multiple dishes per meal. The next step is user control over generated menus.

## Requirements

- replace dish inside MealSlot;
- add dish to MealSlot;
- remove dish from MealSlot;
- preserve Shopping recalculation compatibility;
- keep RecipeComponent pipeline unchanged.

## Constraints

- no MealPlan rewrite;
- use existing MealSlot model;
- maintain legacy compatibility.

## Definition of Done

- backend service implemented;
- API updated;
- tests added;
- documentation updated.
