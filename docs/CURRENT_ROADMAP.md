# TourHub Current Roadmap

## Current Product State

MVP vertical slice is completed:

```
Project
   ↓
Preparation
   ↓
Meal Plan
   ↓
Shopping
   ↓
Purchase Checklist
   ↓
Documents Export
```

Validated:

- Backend tests: pytest — 70 passed
- Frontend build: npm run build — success
- PDF export validated
- Excel export validated
- ZIP package export validated

---

# Completed Technical Debt

## TH-0053.5 — PDF Generator Refactoring

Status: DONE

Completed:

- migrated from reportlab canvas to platypus;
- SimpleDocTemplate;
- Paragraph;
- Table;
- TableStyle;
- footer;
- page numbering.

---

# Technical Debt

## TH-0054 — Document Template Layer

Status: OPEN

Goal:

Create a reusable document template layer for ERP documents.

Problem:

Current document generation works, but document structure is tightly coupled to individual generators.

Impact:

Future document types, club branding and additional export formats will become harder to maintain without a template abstraction.

Planned improvements:

- common document templates;
- shared document DTO structures;
- separation of document layout from generation engine;
- support for PDF/Excel/Print template reuse;
- preparation for club-specific branding.

Priority:

Medium.

Implementation planned after the first complete user scenario.

---

# Current Milestone

## TH-0060 — First User Scenario MVP

Goal:

Create the first complete user journey in single-user mode.

Flow:

```
Create Project
      ↓
Enter participants and duration
      ↓
Generate Preparation
      ↓
View Meal Plan
      ↓
View Shopping List
      ↓
View Purchase Checklist
      ↓
Export Documents
```

Included:

- project creation;
- project parameters;
- preparation generation;
- workspace result display.

Excluded:

- authentication;
- roles;
- clubs;
- permissions.

---

# Next Task

## TH-0060.1 — Project Creation Flow

Backend:

- create project endpoint;
- validate input;
- connect project creation with preparation workflow.

Frontend:

- create project page;
- project form;
- open workspace after creation.

Acceptance criteria:

- user creates project;
- participants and days are saved;
- workspace opens;
- preparation can be started.
