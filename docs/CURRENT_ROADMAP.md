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

- Docker Compose, PostgreSQL, Redis, and Alembic one-head validation;
- backend Ruff, strict mypy, pytest, frontend tests/build/browser acceptance;
- PostgreSQL backup/restore CI;
- LAN-safe routing and responsive navigation.

### Project, recipes, and menu

- project creation, workspace, participants, duration, and meal boundaries;
- recipe/product/Dish catalogues and CSV import;
- persisted Dish roles, compatibility, repeatability, and readiness;
- role-aware generation, diversity, manual-slot preservation, and persisted warnings;
- transactional purchasing recalculation.

### Shopping and packaging through PR #71

- ingredient aggregation and package rounding;
- PurchaseList and PurchaseChecklist persistence;
- required, purchased, and remaining quantity review;
- editable purchase progress;
- package size, package count, total quantity to buy, and surplus;
- responsive Russian UI and browser acceptance.

PR #70 passed exact-head Quality #287. PR #71 passed exact-head Quality #296 and merged as `ed2ab62a70cefbd41425e9cdbaab0f81a6777298`.

## IN PROGRESS

### PR #72 — optional purchasing contact

- nullable PurchaseList field through Alembic `h10004`;
- GET/PATCH contract with trim, clear, and length validation;
- preservation during purchasing recalculation;
- save/clear editor with unit and browser coverage.

## NEXT

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
