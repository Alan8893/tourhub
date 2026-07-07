# TourHub Development Tasks

## Task Management Rules

Each task represents one logical development unit.

Rules:

- one task = one completed increment;
- one commit = one logical task;
- every task must have acceptance criteria;
- completed tasks must not be modified;
- new work is added as new tasks.

---

# Completed Tasks

---

# TH-0001 — Backend Foundation

Status:


DONE


## Goal

Create production-ready backend foundation.

## Completed

Implemented:

- FastAPI application;
- Docker environment;
- PostgreSQL;
- Redis;
- SQLAlchemy setup;
- Alembic;
- configuration system;
- application lifecycle;
- logging.

## Acceptance Criteria

✅ Backend starts  
✅ Docker Compose works  
✅ Database connection works  
✅ Alembic migrations execute  

---

# TH-0002 — Project Documentation Foundation

Status:


DONE


## Goal

Create project documentation base.

Implemented:

- project context;
- architecture description;
- domain description;
- development rules.

---

# TH-0018 — Nutrition Domain Foundation

Status:


DONE


## Goal

Create first business domain.

## Implemented Entities


Product

Recipe

Ingredient

Dish


---

## Database Schema

Created:


products

recipes

ingredients

dishes


Migration:


initial nutrition schema


---

## Acceptance Criteria

✅ ORM models created  
✅ Alembic migration created  
✅ Database schema applied  
✅ Relations configured  

---

# TH-0018.1 — Nutrition Seed Data

Status:


DONE


## Goal

Create initial domain data.

Implemented:

Products:


11 records


Recipes:


5 records


Dishes:


5 records


---

## Acceptance Criteria

✅ Seed executes  
✅ Data available in PostgreSQL  
✅ No duplicate records after repeated execution  

---

# TH-0019 — Shopping List Engine Foundation

Status:


DONE


## Goal

Implement pure calculation engine.

Location:


app/engines/shopping_list.py


---

## Implemented

DTO:


IngredientInput

ShoppingListItem

ShoppingListResult


---

Algorithm:


amount per person
×
participants
×
days
=
required amount


---

## Tests

Created:


tests/engines/test_shopping_list.py


Result:


3 passed


---

# TH-0019.2 — Shopping List Service Foundation

Status:


DONE


## Goal

Connect database models with calculation engine.

Architecture:


ORM

↓

Service

↓

Engine

↓

Result


---

## Implemented

Service:


app/services/shopping_list_service.py


---

## Tests

Created:


tests/services/test_shopping_list_service.py


Result:


1 passed


---

# TH-0019.2.1 — ORM Relationship Cleanup

Status:


DONE


## Goal

Improve SQLAlchemy relationship mapping.

Implemented:


Recipe.ingredients

↕

Ingredient.recipe


using:


back_populates


---

# Current Sprint

---

# TH-0020 — Meal Plan Generator Foundation

Status:


NEXT


## Goal

Create first version of nutrition wizard backend.

---

## Business Scenario

Instructor creates hiking preparation:

Input:


participants

days

start meal


---

System generates:


meal plan

↓

dishes

↓

recipes

↓

shopping list


---

# TH-0020.1 — Meal Plan Domain Model

Status:


PLANNED


## Create Entities

Possible model:


MealPlan

MealPlanDay

MealPlanItem


---

## Acceptance Criteria

- menu structure exists;
- relations defined;
- migration created;
- tests added.

---

# TH-0020.2 — Meal Plan Generator Engine

Status:


PLANNED


## Goal

Generate menu from available dishes.

Rules:

- no repeated dishes;
- respect available recipes;
- provide warning when insufficient data.

---

# TH-0020.3 — Nutrition Wizard API

Status:


PLANNED


## Goal

Create API endpoints.

Expected:


POST /meal-plans/generate


Input:

```json
{
  "participants": 10,
  "days": 5
}

Output:

{
  "menu": [],
  "shopping_list": []
}
Future Tasks
TH-0030 — User Authentication

Planned:

users;
roles;
permissions.

Roles:

Guest

Instructor

Verified Instructor

Administrator
TH-0040 — Hiking Project Module

Planned:

Entity:

Project

Includes:

route;
participants;
preparation status;
documents.
TH-0050 — Equipment Module

Planned:

Features:

equipment lists;
packing;
personal/group inventory.
TH-0060 — Export Module

Planned:

Formats:

PDF;
Excel;
print templates.
Definition of Done

A task is completed only when:

Code

✅ implemented
✅ reviewed
✅ no TODO placeholders

Tests

Required:

business logic tests;
integration tests where required.
Documentation

Updated:

architecture;
domain;
task status.
Git

Required:

Commit format:

type(scope): description

Examples:

feat(nutrition): add meal plan model

test(service): add shopping service tests
Current Project Position

Completed:

Foundation
    ✅

Nutrition Domain
    ✅

Shopping Calculation
    ✅

Shopping Service
    ✅

Current focus:

Meal Plan Generator

Next major milestone:

First complete user scenario:
Generate hiking food plan

---

После замены:

```powershell
git status