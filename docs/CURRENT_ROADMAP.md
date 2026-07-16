# TourHub Current Roadmap

Status date: 2026-07-16

## Product goal

Deliver a stable local MVP for one tourist club without changing the approved architecture.

```text
Project
  → Menu
  → Recipes and dishes
  → Shopping and packaging
  → Equipment
  → Russian PDF and Excel
```

## DONE

### Infrastructure

- Dockerfiles and Docker Compose;
- PostgreSQL and Redis runtime configuration;
- Alembic one-head validation;
- backend Ruff, strict mypy, pytest, frontend tests/build/browser acceptance;
- PostgreSQL backup/restore CI;
- LAN-safe same-origin routing and responsive navigation.

### Projects, recipes, and menu

- project creation, catalogue, workspace, participants, duration, and meal boundaries;
- recipe components, notes, archive/restore, products, CSV import, and Dish catalogue;
- persisted Dish roles, meal compatibility, and repeatability;
- catalogue readiness and Russian classification editor;
- role-aware menu generation with required and optional composition roles;
- same-day uniqueness and calendar-day three-day `main` diversity;
- authoritative manual slots across regeneration;
- persisted generation-warning snapshot through Alembic `h10003`;
- transactional purchasing recalculation after project, menu, and recipe changes.

TH-0061.5 approved rules are merged through PR #69. Operational catalogue classification remains ongoing.

### Shopping foundation

- ingredient aggregation;
- package-rounding calculation;
- PurchaseList and PurchaseChecklist persistence;
- purchased quantity and checked-state persistence;
- checklist-state preservation during recalculation;
- PDF/Excel/package export foundations.

### PR #70 — editable purchase checklist

Merged with exact-head Quality #287:

- product names in checklist responses;
- required, purchased, and non-negative remaining quantities;
- validation against negative purchased quantities;
- editable Russian checklist in the project workspace;
- progress, feedback states, responsive layout, and browser acceptance.

## IN PROGRESS

### PR #71 — package count and surplus review

- product names in PurchaseList responses;
- total purchase quantity derived from package size and package count;
- non-negative package surplus;
- required quantity, package size, package count, total purchase quantity, and surplus in the workspace;
- backend API, frontend helper, and combined purchase browser acceptance;
- no change to aggregation, rounding, persistence, or recalculation algorithms.

## NEXT

### Shopping and packaging

- add optional responsible-person text;
- connect the completed shopping review to the guided preparation sequence.

### Equipment

- persist recipe equipment requirements;
- aggregate maximum simultaneous need;
- support manual overrides;
- recalculate after participant and menu changes.

### Documents and acceptance

- final Russian PDF and Excel;
- club name and logo settings;
- installation/update documentation;
- Docker image/build CI gate;
- complete desktop and mobile release acceptance.

## LATER

- invitation-only registration and roles;
- recipe ownership, variants, publication, and moderation;
- audit log;
- participant profiles, routes, logistics, and load distribution;
- warehouse balances and price aggregation.

Multi-tenant support and microservices remain prohibited.
