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

## IN PROGRESS

### PR #79 — operator installation and update runbooks

- document prerequisites, first startup, health, migration, LAN, port, and volume checks;
- provide backup-first update and recovery procedures;
- add host-side custom-format PostgreSQL backup and confirmed restore commands;
- create a pre-restore safety backup when replacing an existing database;
- define rollback boundaries and prohibit destructive volume deletion;
- link operator entry points from README;
- validate scripts, commands, links, and Docker Compose syntax in a focused workflow.

## NEXT

- add Docker image build and runtime smoke validation;
- add PostgreSQL migration upgrade/downgrade smoke;
- complete the final release workflow and checklist.

## LATER

- invitation-only registration and roles;
- recipe ownership, variants, publication, and moderation;
- audit log;
- participant profiles, routes, logistics, and load distribution;
- warehouse balances and price aggregation.

Multi-tenant support and microservices remain prohibited.
