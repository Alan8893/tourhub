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

### Core preparation through PR #72

- project creation, workspace, participants, duration, and meal boundaries;
- catalogues and CSV import;
- role-aware menu generation and manual editing;
- persisted shopping, package review, surplus, and purchasing contact;
- transactional purchasing recalculation.

### Equipment through merged PR #74

- recipe equipment requirements through Alembic `h10005`;
- persisted maximum-simultaneous EquipmentList projection;
- calculated baseline and user-controlled final quantity through `h10006`;
- manual additions, quantity overrides, and removals;
- preservation during repeated preparation and recalculation;
- refresh after meal, Dish recipe, participant, and full-menu changes;
- Russian editing UI with browser and mobile acceptance.

PR #74 passed Quality #350 and merged as `4bde39c480776d46bf25894cb77602a4e1adb0cd`.

## IN PROGRESS

### PR #75 — recipe-equipment mutation refresh

- refresh prepared project equipment lists after requirement POST, PUT, or DELETE;
- keep the requirement mutation and derived refresh in one transaction;
- preserve overrides, removals, and manual rows;
- leave unprepared projects unchanged;
- cover multiple affected projects and rollback on refresh failure;
- enforce the service in stabilized Ruff and strict mypy gates.

The functional head passed Quality #353 before documentation synchronization.

## NEXT

- include equipment in final Russian PDF and Excel;
- add club name and logo settings;
- complete guided desktop and mobile acceptance;
- add installation/update documentation;
- add Docker build and migration smoke gates;
- complete the final release workflow.

## LATER

- invitation-only registration and roles;
- recipe ownership, variants, publication, and moderation;
- audit log;
- participant profiles, routes, logistics, and load distribution;
- warehouse balances and price aggregation.

Multi-tenant support and microservices remain prohibited.
