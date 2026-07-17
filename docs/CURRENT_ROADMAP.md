# TourHub Current Roadmap

Status date: 2026-07-17

## Product goal

Deliver a stable local MVP for one tourist club without changing the approved architecture.

```text
Project
  → Menu
  → Recipes and dishes
  → Shopping and packaging
  → Equipment
  → Branded Russian PDF and Excel
```

## DONE

### Infrastructure

- Docker Compose, PostgreSQL, Redis, and Alembic one-head validation;
- backend Ruff, strict mypy, pytest, frontend tests/build/browser acceptance;
- PostgreSQL backup/restore CI;
- LAN-safe routing and responsive navigation.

### Preparation workflow through merged PR #76

- project creation, workspace, participants, duration, and meal boundaries;
- catalogues, CSV import, role-aware menu generation, and manual editing;
- persisted shopping, packaging, surplus, and purchasing contact;
- persisted equipment requirements, project overrides, and transactional recalculation;
- Russian purchase and equipment PDF/Excel plus five-file ZIP package;
- focused document quality and real-browser desktop/mobile acceptance.

PR #76 passed exact-head Quality #397 and Document Quality #31 and merged as `51ea7785f12e8d1d30b2768284b6fddbb0117872`.

## IN PROGRESS

### PR #77 — persistent club branding

- persist singleton club name and optional logo through Alembic `h10007`;
- validate PNG/JPEG MIME, decoded image content, size, and dimensions;
- provide Russian settings UI with preview and removal;
- apply one consistent branding snapshot to every generated project document;
- embed proportional logos in PDF and Excel without shifting existing tables;
- verify settings API, document metadata/content, exact browser PUT body, screenshot, and 360 px layout;
- enforce branding modules in focused Ruff, strict mypy, and tests.

The functional head passed Quality #412 and Document Quality #45 before documentation synchronization.

## NEXT

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
