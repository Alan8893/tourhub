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
  → Guided release acceptance
  → Operator installation and update path
  → Production-like Docker runtime
```

## DONE

### Infrastructure baseline

- Docker Compose, PostgreSQL 18, Redis, and Alembic one-head validation;
- backend Ruff, strict mypy, pytest, frontend tests/build/browser acceptance;
- PostgreSQL backup/restore CI;
- LAN-safe routing and responsive navigation.

### Guided preparation through merged PR #78

- project creation, workspace, participants, duration, and meal boundaries;
- catalogues, CSV import, role-aware menu generation, and manual editing;
- persisted shopping, packaging, surplus, and purchasing contact;
- persisted equipment requirements, project overrides, and transactional recalculation;
- Russian purchase and equipment PDF/Excel plus complete ZIP package;
- persistent single-club branding through Alembic `h10007`;
- reload-safe preparation state and equipment-aware completion;
- full create → menu → prepare → reload → branded ZIP desktop/mobile acceptance.

PR #77 merged as `18d4fabde3eda6c83c0c0f998e870a6f043e8dec`. PR #78 passed retargeted exact-head Quality #431, Document Quality #63, and Guided Release Acceptance #14 and merged as `6332ef5f86973c7832e92dc1ef0a681cc4e17d1e`.

### Operator installation and update through merged PR #79

- documented prerequisites, first startup, health, migration, LAN, port, and volume checks;
- added backup-first update and recovery procedures;
- added host-side custom-format PostgreSQL backup and confirmed restore commands;
- created a pre-restore safety backup when replacing an existing database;
- defined rollback boundaries and prohibited destructive volume deletion;
- linked operator entry points from README;
- validated scripts, commands, links, and Docker Compose syntax in Operator Docs.

PR #79 passed exact-head Quality #436, Document Quality #67, Guided Release Acceptance #18, and Operator Docs #4 and merged as `99d9c2d985b8a21c62fe148e07e08b3632ef961a`.

## IN PROGRESS

### Draft PR #80 — Docker release runtime validation

- add a standalone release Compose stack without source bind mounts;
- build the frontend into a production Nginx image;
- keep PostgreSQL and Redis internal while preserving the named database volume;
- add explicit frontend/backend health checks and same-origin API proxying;
- build and start a disposable stack from a clean environment;
- verify the app shell, API health, project creation, migration head, and persistence after restart;
- capture focused Docker diagnostics and remove the disposable stack unconditionally.

## NEXT

- add PostgreSQL migration upgrade/downgrade smoke;
- complete the final release workflow and checklist.

## LATER

- invitation-only registration and roles;
- recipe ownership, variants, publication, and moderation;
- audit log;
- participant profiles, routes, logistics, and load distribution;
- warehouse balances and price aggregation.

Multi-tenant support and microservices remain prohibited.
