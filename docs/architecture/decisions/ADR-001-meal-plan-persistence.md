# ADR-001 — MealPlan Persistence

Status:

Accepted

## Decision

MealPlan must be stored as a domain entity.

## Reason

Future multi-user mode requires:

- multiple instructors accessing the same plan;
- editing;
- approval workflow;
- audit history.

## Consequence

Generation creates persistent MealPlan data instead of returning only calculated output.
