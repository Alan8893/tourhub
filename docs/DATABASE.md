# TourHub Database Documentation

## Overview

TourHub uses PostgreSQL as the primary database.

Current version:


PostgreSQL 16


Database migrations are managed using:


Alembic


---

# Database Principles

## Migration First

Any database structure change must go through Alembic.

Forbidden:

- manual production schema changes;
- editing database directly without migration.

Correct workflow:


Modify ORM Model

    ↓

Generate Migration

    ↓

Review Migration

    ↓

Apply Migration


---

# Current Schema

Current database contains:


alembic_version

products

recipes

ingredients

dishes


---

# Schema Overview


products
|
|
ingredients
|
|
recipes
|
|
dishes


---

# Tables

---

# products

## Purpose

Stores purchasable products.

Examples:


Rice

Buckwheat

Meat

Tea

Sugar


---

## Structure

| Column | Type | Description |
|---|---|---|
| id | String | Primary key |
| name | String | Product name |
| category | String | Product category |
| unit | String | Measurement unit |
| package_size | Integer | Package weight |

---

## Example


name:

Buckwheat

unit:

gram

package_size:

900


---

# recipes

## Purpose

Stores food recipes.

A recipe describes composition of a dish.

Example:


Camp pilaf


---

## Structure

| Column | Type | Description |
|---|---|---|
| id | String | Primary key |
| name | String | Recipe name |

---

# ingredients

## Purpose

Connects recipes with products.

Defines required product quantity.

---

## Structure

| Column | Type | Description |
|---|---|---|
| id | String | Primary key |
| recipe_id | String | Recipe reference |
| product_id | String | Product reference |
| amount_per_person | Integer | Amount per person |

---

## Relations


Ingredient

|

+---- Recipe

|

+---- Product

---

# dishes

## Purpose

Represents menu items.

A dish references a recipe.

Example:


Dinner:

Camp pilaf


---

## Structure

| Column | Type | Description |
|---|---|---|
| id | String | Primary key |
| name | String | Dish name |
| recipe_id | String | Recipe reference |

---

# ORM Mapping

Location:


backend/app/models


Current models:


product.py

recipe.py

ingredient.py

dish.py


---

# Relationships

## Product

One product can be used in many ingredients.


Product

1

↓

N

Ingredient


---

## Recipe

One recipe contains many ingredients.


Recipe

1

↓

N

Ingredient


Implemented:

```python
Recipe.ingredients

and

Ingredient.recipe

with:

back_populates
Dish

One dish uses one recipe.

Dish

N

↓

1

Recipe
Alembic

Location:

backend/alembic
Current Migration

Initial nutrition schema:

0d101bb77375

Created:

products

recipes

ingredients

dishes
Migration Commands
Create migration

From:

backend/

run:

python -m alembic revision --autogenerate -m "description"
Apply migrations
python -m alembic upgrade head
Check current version

Inside PostgreSQL:

select * from alembic_version;
Database Development Rules
Rule 1

ORM models are the source of database structure.

Rule 2

Every schema change requires migration.

Rule 3

Migrations must be reviewed before applying.

Rule 4

Do not store business logic inside database models.

Models describe:

structure;
relations;
persistence.

Business rules belong to:

services

engines
Future Database Extensions

Planned entities:

Project

Central hiking preparation entity.

Possible tables:

projects

participants

routes
Meal Plan

Planned:

meal_plans

meal_plan_days

meal_plan_items
Equipment

Planned:

equipment

equipment_items

packing_lists
Users

Planned:

users

roles

clubs

permissions
Current Database Status

Implemented:

Products        ✅

Recipes         ✅

Ingredients     ✅

Dishes          ✅

Migrations      ✅

Seed Data       ✅

Next database extension:

Meal Plan Domain