# TourHub Roadmap

## Product Vision

TourHub is planned as a complete ERP platform for tourist clubs.

The product should help clubs manage the entire lifecycle of a hiking trip:


Idea

↓

Trip Preparation

↓

Route Planning

↓

Food Planning

↓

Equipment Preparation

↓

Execution

↓

Reports


---

# Current Phase

## Phase 1 — MVP Foundation

Status:


IN PROGRESS


Goal:

Create a working system that can automatically prepare food requirements for a hiking trip.

---

## Completed

### Backend Foundation

Status:


DONE


Implemented:

- FastAPI backend;
- PostgreSQL;
- Redis;
- SQLAlchemy;
- Alembic;
- Docker environment;
- configuration system.

---

### Nutrition Domain

Status:


DONE


Implemented:


Product

Recipe

Ingredient

Dish


---

### Shopping Calculation

Status:


DONE


Implemented:


Recipe

↓

Ingredients

↓

Shopping List


---

# Phase 2 — Nutrition Wizard

Status:


NEXT


Goal:

Create the first complete user scenario.

Scenario:


Instructor enters:

participants count
hiking days
starting meal

↓

System generates:

menu
dishes
recipes
shopping list

---

# TH-0020 — Meal Plan Generator

## Goal

Create automatic meal planning.

---

## Components

### Meal Plan Domain

Entities:


MealPlan

MealPlanDay

MealPlanItem


---

### Generator Engine

Responsibilities:

- choose dishes;
- avoid repetitions;
- handle insufficient dish database;
- generate warnings.

---

### Meal Plan Service

Responsibilities:

- load available dishes;
- execute generator;
- save result.

---

# Phase 3 — Shopping & Preparation

Status:


PLANNED


Goal:

Convert calculations into real preparation workflows.

---

## Features

### Purchase List

Capabilities:

- product quantities;
- package sizes;
- total purchasing amount.

Example:


Buckwheat:

required:
3200 g

package:

900 g

result:

4 packages


---

### Packaging List

Capabilities:

- divide products into packages;
- assign weight;
- prepare group bags.

---

### Export

Formats:


PDF

Excel

Print


---

# Phase 4 — Hiking Project Management

Status:


PLANNED


Goal:

Create central trip management.

---

## Project Entity

Main aggregate:


Project


Contains:


Route

Participants

Meal Plan

Equipment

Documents


---

## Route Module

Planned:

- route description;
- map links;
- coordinates;
- difficulty;
- comments.

---

# Phase 5 — User System

Status:


PLANNED


---

## Authentication

Features:

- registration;
- login;
- sessions;
- permissions.

---

## Roles

### Guest

Can:

- view public information.

---

### Instructor

Can:

- create trips;
- prepare hikes;
- generate lists.

---

### Verified Instructor

Can:

- publish activities;
- manage club resources.

---

### Administrator

Can:

- manage clubs;
- manage users;
- configure system.

---

# Phase 6 — Multi Club ERP

Status:


PLANNED


Goal:

Support multiple tourist organizations.

---

Architecture:


Club

|

Users

|

Projects

|

Trips


---

# Phase 7 — Advanced Features

Status:


FUTURE


Possible features:

## Analytics

- trip statistics;
- expenses;
- consumption analysis.

---

## Inventory

- equipment database;
- availability;
- history.

---

## Mobile Application

Possible:

- checklist;
- offline access;
- trip assistant.

---

# Development Principles

## Incremental Development

Each milestone must create working value.

---

## Business Logic First

Priority:


Domain

↓

Service

↓

API

↓

UI


---

## Keep Calculations Pure

All algorithms should remain:

- deterministic;
- isolated;
- testable.

---

# Current Position

Completed:


Backend Foundation ✅

Nutrition Domain ✅

Shopping Engine ✅

Shopping Service ✅


Current:


Meal Plan Generator


Next user-visible milestone:


Generate hiking food plan automatically