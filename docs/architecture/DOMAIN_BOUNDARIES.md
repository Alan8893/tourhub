# TourHub Domain Boundaries

Status:

Accepted

Date:

2026-07-09

---

# Purpose

This document defines high-level product domains and prevents mixing responsibilities between modules.

TourHub is built around the Project aggregate.

```
Project
 |
 +-- Nutrition
 |
 +-- Shopping
 |
 +-- Documents
 |
 +-- Logistics (future)
```

---

# Project as the root business object

A hiking preparation project contains related preparation processes.

The Project does not own all logic directly. Each domain has its own responsibility.

---

# Nutrition Domain

Current implementation focus.

Responsibilities:

- meal planning;
- menu generation;
- dish selection;
- food restrictions;
- purchase calculation input.

Does not manage:

- participants;
- equipment allocation;
- transport logistics.

---

# Shopping Domain

Responsibilities:

- ingredient aggregation;
- purchase lists;
- packaging;
- procurement workflow.

Receives data from Nutrition.

---

# Documents Domain

Responsibilities:

- PDF generation;
- Excel export;
- printable documents.

---

# Future Logistics Domain

Status:

Planned, not implemented.

Responsibilities:

- support vehicle information;
- public equipment inventory;
- equipment distribution between teams;
- carrying load balance.

Example future scenario:

```
Project
 |
 Logistics
 |
 Teams
 |
 Equipment Allocation
```

The logistics domain is intentionally separated from Nutrition.

However, future logistics constraints may influence nutrition generation:

- maximum carried weight;
- absence of support vehicle;
- product transport limitations.

---

# Architectural rule

Future domains are documented before implementation.

Do not create database entities until the current domain requires them.
