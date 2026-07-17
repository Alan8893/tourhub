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

## IN PROGRESS

### PR #80 — Docker release runtime validation

- production-like Docker image and runtime validation;
- clean environment startup checks;
- release Compose verification.

### TH-0073 — MVP completeness audit

- compare Product Specification against implemented functionality;
- identify true release blockers before final release hardening;
- separate required MVP features from intentionally deferred scope.

## NEXT

- complete MVP completeness audit;
- implement approved missing user-facing MVP functionality if required;
- postpone final migration downgrade smoke and release checklist until the MVP boundary is confirmed.

## LATER

- invitation-only registration and roles;
- recipe ownership, variants, publication, and moderation;
- audit log;
- participant profiles, routes, logistics, and load distribution;
- warehouse balances and price aggregation.

Multi-tenant support and microservices remain prohibited.
