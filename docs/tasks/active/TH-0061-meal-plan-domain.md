# TH-0061.3 — MealPlan Domain Expansion

Status:

PLANNED

## Goal

Create a persistent meal plan domain suitable for real hiking workflows.

## Decisions

MealPlan is a business document, not a temporary calculation result.

It must support:

- multiple instructors viewing the same plan;
- editing;
- approval workflow;
- historical state.

## Target Model

Project
 |
 MealPlan
 |
 MealPlanDay
 |
 MealSlot
 |
 Dishes

## Requirements

- Support incomplete first and last hiking days.
- Support one-day hikes.
- Store generated menu structure.

## Acceptance Criteria

- Meal plan persisted in database.
- Daily structure exists.
- Generation creates stored entities.
