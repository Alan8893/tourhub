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

### Equipment through merged PR #75

- recipe equipment requirements through Alembic `h10005`;
- persisted maximum-simultaneous EquipmentList projection;
- calculated baseline and user-controlled final quantity through `h10006`;
- manual additions, quantity overrides, and removals;
- preservation during repeated preparation and recalculation;
- refresh after meal, Dish recipe, participant, full-menu, and direct requirement changes;
- multi-project transactional fan-out and rollback protection;
- Russian editing UI with browser and mobile acceptance.

PR #75 passed exact-head Quality #355 and merged as `d048378c2a4e1d1ac5c57aebe66ba8154fa7eac0`.

## IN PROGRESS

### PR #76 — Russian purchase and equipment documents

- localize purchase PDF and Excel output;
- export final equipment quantities to Russian PDF and Excel;
- show calculated baseline and manual/override source labels;
- exclude removed equipment rows;
- expose equipment PDF and Excel download endpoints;
- add Russian purchase, equipment, and full-package download controls;
- include purchase PDF, purchase Excel, purchase print, equipment PDF, and equipment Excel in the ZIP package;
- verify content, API responses, exact browser requests, screenshot, and 360 px layout;
- enforce document modules with focused Ruff, strict mypy, and tests.

The functional head passed Quality #389 and Document Quality #23 before documentation synchronization.

## NEXT

- add club name and logo settings and apply document branding;
- complete guided desktop and mobile release acceptance;
- add installation and update documentation;
- add Docker image/build and PostgreSQL migration smoke gates;
- complete the final release workflow.

## LATER

- invitation-only registration and roles;
- recipe ownership, variants, publication, and moderation;
- audit log;
- participant profiles, routes, logistics, and load distribution;
- warehouse balances and price aggregation.

Multi-tenant support and microservices remain prohibited.
