# ADR-009 — Future Expedition Logistics Domain

Status:

Planned

Date:

2026-07-09

---

# Context

TourHub may later require support for expedition logistics.

Examples:

- trips with support vehicles;
- trips without support vehicles;
- public equipment distribution;
- load balancing between teams.

---

# Decision

Logistics is a separate future domain.

It is not part of MealPlan or Nutrition.

Future structure:

```
Project
 |
 Logistics
 |
 + Transport
 + Equipment
 + Teams
 + Carry Allocation
```

---

# Example use case

Group:

- 6 participants;
- 2 instructors;
- 4 kayaks.

Public equipment:

- tents;
- shelters;
- cooking equipment;
- repair kit;
- first aid kit.

Future system may distribute equipment between teams to avoid overload.

---

# Nutrition relation

Logistics may provide constraints in the future:

- maximum carried weight;
- absence of support vehicle;
- product transportation limitations.

Nutrition must not directly depend on Logistics implementation.

---

# Current scope

No implementation.
No database entities.
No API.

Only architecture boundary is fixed.
