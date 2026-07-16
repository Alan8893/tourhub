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

### Shopping and packaging through PR #72

- ingredient aggregation and package rounding;
- PurchaseList and PurchaseChecklist persistence;
- required, purchased, remaining, package-count, total-purchase, and surplus review;
- editable purchase progress;
- optional purchasing contact preserved through recalculation;
- responsive Russian UI and browser acceptance.

PR #72 passed exact-head Quality #315 and merged as `3d827a7f9a68fe3d27ac333a4290053e407d3a2d`.

## IN PROGRESS

### PR #73 — equipment requirements and aggregation

- persist equipment requirements on recipes through Alembic `h10005`;
- add validated recipe requirement CRUD and archived-recipe read-only behavior;
- persist one EquipmentList per project and meal plan;
- sum identical equipment within one meal occurrence;
- select the maximum simultaneous quantity across meal occurrences;
- refresh the persisted list safely on repeated preparation;
- show requirements in the recipe editor and the generated list in the project workspace;
- cover backend, frontend, production build, browser acceptance, 360 px no-overflow, and PostgreSQL backup/restore.

The functional head passed exact-head Quality #331 before documentation synchronization.

## NEXT

### Equipment completion

- support manual additions, removals, and quantity overrides on the project EquipmentList;
- preserve manual overrides while recalculating generated quantities;
- refresh equipment after participant, menu, and recipe changes.

### Documents and acceptance

- final Russian PDF and Excel including equipment;
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
