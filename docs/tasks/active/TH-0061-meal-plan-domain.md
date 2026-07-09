# TH-0061.3 — MealPlan Domain Expansion

Status:

IN PROGRESS

## Goal

Create a persistent meal plan domain suitable for real hiking workflows.

## Completed

- Meal schedule engine created.
- Project meal context connected.
- Support for first and last meal boundaries added.
- API response prepared for grouped meals.
- Multiple dishes per meal generation implemented.

## Decisions

MealPlan is a business document, not a temporary calculation result.

It must support:

- multiple instructors viewing the same plan;
- editing;
- approval workflow;
- historical state.

## Current Model

Project
 |
 MealPlan
 |
 MealPlanDay
 |
 MealPlanItem[]
 |
 Dishes

Multiple MealPlanItem records with the same day and meal_type represent one meal composition.

## Requirements

- Support incomplete first and last hiking days.
- Support one-day hikes.
- Store generated menu structure.
- Support multiple dishes in one meal.

## Acceptance Criteria

- Meal plan persisted in database.
- Daily structure exists.
- Generation creates stored entities.
- Frontend can display grouped meals.

## Remaining Work

- Frontend MealSlot display.
- Real meal composition rules (main dish, drink, additional dishes).
- Instructor editing workflow.
