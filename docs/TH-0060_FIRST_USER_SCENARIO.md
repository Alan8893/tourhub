# TH-0060 — First User Scenario MVP

## Goal

Create the first complete user journey in TourHub.

The user must be able to create a hiking project, enter basic parameters, generate preparation data and review the result.

---

## MVP Scope

Single-user mode.

This milestone does not include:

- authentication;
- user accounts;
- roles;
- clubs;
- permissions.

---

## User Flow

```
Create Project
      ↓
Preparation
      ↓
Meal Plan
      ↓
Shopping List
      ↓
Purchase Checklist
      ↓
Documents
```

---

## Project Creation Input

Required fields:

- project name;
- number of participants;
- number of hiking days;
- first meal of the hike.

---

## Expected Result

After generation the user can view:

- project information;
- generated meal plan;
- shopping list;
- purchase checklist;
- document exports.

---

## Architecture

The implementation reuses existing domains:

```
Project
Preparation
MealPlan
Shopping
Purchase
Documents
```

No new architectural layer is introduced.

---

## Acceptance Criteria

- user can create a project;
- project parameters are saved;
- preparation workflow can be started;
- generated meal plan is displayed;
- shopping data is displayed;
- documents remain available.
