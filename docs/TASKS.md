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
# Tasks

## Completed

### TH-0033
Frontend Foundation

Status:
DONE


### TH-0034
Purchase Workflow Dashboard

Status:
DONE


### TH-0035
Environment Stabilization

Status:
DONE


---

# Current

## TH-0036
Project Workspace ERP UI


Goal:

Создать рабочее место инструктора.


Structure:

Project Workspace

├── Project Info
├── Meal Plan
├── Shopping List
├── Packaging
├── Purchase Checklist
└── Documents


---

# Future

TH-0037 Authentication

TH-0038 User Roles

TH-0039 Club Management

TH-0040 Route Cards

---

# TH-0042 — Documents Workflow Integration

Status:

DONE

## Goal

Connect Project workflow with document generation.

Workflow:

Project
 |
 +-- MealPlan
 |
 +-- PurchaseList
 |
 +-- PurchaseChecklist
 |
 +-- Documents


## Implemented

Added:

backend/app/services/project_document_service.py

Responsibilities:

- project document orchestration;
- purchase document generation;
- connection between Project workflow and Document Engine.


## API

Added endpoints:

GET /api/v1/projects/{project_id}/documents/purchase/pdf

GET /api/v1/projects/{project_id}/documents/purchase/excel

GET /api/v1/projects/{project_id}/documents/purchase/print


## Architecture

Implemented:

Project
 ↓
ProjectDocumentService
 ↓
Document Engine
 ↓
PDF / Excel / Print


## Repository Changes

Updated:

backend/app/modules/projects/repositories/project_repository.py

Added loading:

Project
 |
 purchase_lists

to support document generation workflow.


## Tests

Added:

backend/tests/services/test_project_document_service.py

backend/tests/api/test_project_documents_api.py

backend/tests/api/test_project_documents_success_api.py


Coverage:

✅ PDF generation  
✅ Excel generation  
✅ Print generation  
✅ Error contract validation  
✅ Project document workflow


## Acceptance Criteria

✅ Project can generate purchase documents  
✅ PDF export works  
✅ Excel export works  
✅ Print export works  
✅ API endpoints tested  
✅ Regression tests passed


Verification:

68 passed

# TH-0043 — Project Document Package Workflow

Status:

DONE

## Goal

Create unified project document package export.

## Implemented

Added:

backend/app/services/project_document_package_service.py

Responsibilities:

- aggregate project documents;
- create ZIP package;
- reuse existing document generators.


## API

Added:

GET /api/v1/projects/{project_id}/documents/package


Response:

application/zip


## Package Content

Included:

- purchase_list.pdf
- purchase_list.xlsx
- purchase_list.txt


## Architecture

Project

↓

ProjectDocumentPackageService

↓

ProjectDocumentService

↓

Document Engine

↓

ZIP Package


## Tests

Added:

backend/tests/api/test_project_document_package_api.py


Coverage:

✅ package generation  
✅ ZIP content validation  
✅ API success response  
✅ API error contract


## Acceptance Criteria

✅ Project package generated  
✅ ZIP export works  
✅ Existing document workflow reused  
✅ Regression tests passed


Verification:

70 passed

---

# TH-0050.1 — Frontend API Foundation

Status:

DONE

## Goal

Create frontend API foundation layer.

## Implemented

Added:

frontend/src/shared/api/client.ts

Responsibilities:

- centralized Axios client;
- API base URL configuration;
- HTTP interceptor foundation.


Added:

frontend/src/shared/api/errors.ts

Responsibilities:

- API error contract;
- error normalization.


Added:

frontend/src/vite-env.d.ts

Responsibilities:

- Vite environment typings;
- TypeScript support for import.meta.env.


## Verification

Frontend build:

npm run build

Result:

✅ TypeScript compilation passed  
✅ Vite production build passed


## Acceptance Criteria

✅ Shared API client created  
✅ API error handling foundation created  
✅ Vite typings configured  
✅ Production build successful

# TH-0050.2 — Router Foundation

Status:

DONE

## Goal

Create frontend routing foundation.

## Implemented

Added:

frontend/src/app/router/routes.tsx

Responsibilities:

- centralized route configuration;
- application navigation foundation.


Added:

frontend/src/app/router/index.tsx

Responsibilities:

- router entry point;
- route rendering.


Updated:

frontend/src/app/App.tsx

Responsibilities:

- connect application router.


## Verification

Frontend build:

npm run build

Result:

✅ TypeScript compilation passed
✅ Vite production build passed


## Acceptance Criteria

✅ Router layer created
✅ Routes configuration created
✅ Existing workspace flow preserved
✅ Production build successful

# TH-0050.3 — Feature Structure Normalization

Status:

DONE

## Goal

Normalize frontend feature boundaries.

## Implemented

Added:

- feature barrel exports;
- shared feature entry points;
- TypeScript/Vite path alias.

Updated:

- project imports;
- project-workspace imports.

## Verification

npm run build

Result:

✅ TypeScript compilation passed
✅ Vite production build passed

## Acceptance Criteria

✅ Feature boundaries created
✅ Import coupling reduced
✅ Build successful

---

# TH-0050.4 — Environment + Build Hardening

Status:

DONE

## Goal

Prepare frontend environment configuration for production workflow.

## Implemented

Added:

- frontend/.env.example;
- frontend/src/shared/config/env.ts.

Updated:

- frontend/src/shared/api/client.ts.

## Verification

npm run build

Result:

✅ TypeScript compilation passed  
✅ Vite production build passed

## Acceptance Criteria

✅ Environment template created  
✅ Centralized config layer created  
✅ API client uses config layer  
✅ Production build successful

---

# TH-0051 — Frontend Application Shell

Status:

DONE

## Goal

Create frontend ERP application shell.

## Implemented

Added:

- frontend/src/app/layout/AppLayout.tsx;
- frontend/src/app/layout/Header.tsx;
- frontend/src/app/layout/Sidebar.tsx.

Updated:

- frontend/src/app/router/routes.tsx.

## Architecture

Application

↓

AppLayout

↓

Router Outlet

↓

Pages

↓

Features


## Verification

npm run build

Result:

✅ TypeScript compilation passed
✅ Vite production build passed

## Acceptance Criteria

✅ Application shell created
✅ Layout integrated with router
✅ Navigation foundation created
✅ Production build successful


---

# TH-0052 — Frontend Project Module Integration

Status:

DONE

## Goal

Integrate Project feature workflow into frontend workspace.

## Implemented

Updated:

- frontend/src/features/project-workspace/ProjectWorkspace.tsx

Changes:

- removed hardcoded project id;
- added route parameter integration;
- connected workflow composition layer.

Added:

- frontend/src/features/project-workspace/components/ProjectWorkflowPanel.tsx

Responsibilities:

- project workflow composition;
- preparation for feature modules.


## Architecture

ProjectWorkspace

↓

Workflow Panel

↓

Feature Modules


## Verification

npm run build

Result:

✅ TypeScript compilation passed  
✅ Vite production build passed


## Acceptance Criteria

✅ Project id comes from route
✅ Workflow composition created
✅ Existing project flow preserved
✅ Production build successful

---

# TH-0053.1 — Workflow Feature Boundaries

Status:

DONE

## Goal

Create frontend feature boundaries for project workflows.

## Implemented

Added:

- frontend/src/features/meal-plan/components/MealPlanWidget.tsx
- frontend/src/features/shopping/components/ShoppingWidget.tsx
- frontend/src/features/purchase/components/PurchaseWidget.tsx
- frontend/src/features/documents/components/DocumentsWidget.tsx


## Architecture

ProjectWorkspace

↓

Workflow Features

↓

Domain Feature Modules


## Verification

npm run build

Result:

✅ TypeScript compilation passed  
✅ Vite production build passed


## Acceptance Criteria

✅ Feature boundaries created  
✅ Workflow UI separated from workspace  
✅ Backend unchanged  
✅ Production build successful

---

# TH-0053.2 — Workflow Feature Integration

Status:

DONE

## Goal

Integrate workflow feature widgets into Project Workspace.

## Implemented

Updated:

- frontend/src/features/project-workspace/components/WorkflowModules.tsx


Integrated:

- MealPlanWidget
- ShoppingWidget
- PurchaseWidget
- DocumentsWidget


Added feature public exports:

- frontend/src/features/meal-plan/index.ts
- frontend/src/features/shopping/index.ts
- frontend/src/features/purchase/index.ts
- frontend/src/features/documents/index.ts


## Architecture

ProjectWorkspace

↓

WorkflowModules

↓

Feature Widgets

↓

Domain Features


## Verification

npm run build

Result:

✅ TypeScript compilation passed
✅ Vite production build passed


## Acceptance Criteria

✅ Workflow widgets integrated
✅ Feature public API created
✅ Workspace remains orchestration layer
✅ Production build successful

---

# TH-0053.3.1 — Project Workflow Context

Status:

DONE

## Goal

Create shared workflow state layer between Project Workspace and feature modules.

## Implemented

Added:

- frontend/src/features/project-workflow/context/ProjectWorkflowProvider.tsx
- frontend/src/features/project-workflow/index.ts


Updated:

- frontend/src/features/project-workspace/ProjectWorkspace.tsx


## Architecture

ProjectWorkspace

↓

ProjectWorkflowProvider

↓

Workflow Features

↓

Feature Widgets


## Stored State

Provider stores:

- projectId
- preparationResult


## Verification

npm run build

Result:

✅ TypeScript compilation passed  
✅ Vite production build passed


## Acceptance Criteria

✅ Workflow state layer created  
✅ ProjectWorkspace integrated  
✅ Feature boundaries preserved  
✅ Backend contract unchanged  
✅ Production build successful