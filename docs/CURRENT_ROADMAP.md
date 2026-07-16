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

### Project, menu, and shopping through PR #72

- project creation, workspace, participants, duration, and meal boundaries;
- recipe/product/Dish catalogues and CSV import;
- role-aware menu generation, diversity, manual-slot preservation, and warnings;
- PurchaseList and PurchaseChecklist persistence;
- editable purchasing, package counts, total purchase quantities, surplus, and purchasing contact;
- transactional purchasing recalculation.

### Equipment foundation — merged PR #73

- persisted recipe equipment requirements through Alembic `h10005`;
- validated CRUD and archived-recipe read-only behavior;
- persisted project EquipmentList;
- sum within one meal occurrence and maximum simultaneous aggregation across occurrences;
- safe repeated preparation;
- Russian recipe and project UI with browser and mobile acceptance.

PR #73 passed exact-head Quality #334 and merged as `cf4d39b9d7834e13763a4a02b8b2a13f25e44f5a`.

## IN PROGRESS

### PR #74 — project equipment overrides

- add Alembic `h10006` for calculated baseline, manual state, and removal tombstones;
- support manual project additions, quantity overrides, and removals;
- preserve user decisions while recalculating the generated baseline;
- refresh equipment after meal-slot edits, Dish recipe changes, participant changes, repeated preparation, and full menu regeneration;
- provide Russian editing controls and real-browser CRUD/refetch/mobile acceptance;
- include all new modules in stabilized Ruff and strict mypy gates.

The functional head passed Quality #349 before documentation synchronization.

## NEXT

### Equipment and documents

- refresh EquipmentList after direct recipe-equipment requirement mutations;
- include equipment in final Russian PDF and Excel;
- add club name and logo settings;
- complete desktop and mobile guided-preparation acceptance.

### Release engineering

- installation/update documentation;
- Docker image/build CI gate;
- PostgreSQL migration upgrade/downgrade smoke;
- final release workflow.

## LATER

- invitation-only registration and roles;
- recipe ownership, variants, publication, and moderation;
- audit log;
- participant profiles, routes, logistics, and load distribution;
- warehouse balances and price aggregation.

Multi-tenant support and microservices remain prohibited.
