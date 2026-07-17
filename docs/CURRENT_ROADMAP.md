# TourHub Current Roadmap

Status date: 2026-07-17

## Product goal

Deliver the approved local MVP for one tourist club without changing the approved architecture.

```text
Project preparation baseline
  → Production-like Docker runtime
  → Product completeness audit
  → System Settings foundation
  → Access and roles
  → Recipe ownership and lifecycle
  → Central domain safety
  → Actor-aware audit
  → Consolidated Russian exports
  → Product acceptance and feature freeze
  → Final migration and release gates
```

## DONE

### Infrastructure and guided preparation

- Docker Compose, PostgreSQL 18, Redis, and Alembic one-head validation;
- backend Ruff, strict mypy, pytest, frontend tests/build/browser acceptance;
- PostgreSQL backup/restore CI;
- project creation, role-aware menu generation and authoritative manual editing;
- persisted shopping, packaging, equipment, recalculation, overrides, and readiness;
- singleton club branding and Russian purchase/equipment PDF, Excel, print, and ZIP;
- desktop/mobile create → menu → prepare → reload → branded ZIP acceptance.

PR #77 merged as `18d4fabde3eda6c83c0c0f998e870a6f043e8dec`. PR #78 merged as `6332ef5f86973c7832e92dc1ef0a681cc4e17d1e`.

### Operator path through merged PR #79

- installation, health, migration, LAN, port, and volume checks;
- backup-first update and recovery procedures;
- host-side PostgreSQL backup and confirmed restore;
- rollback boundaries and Operator Docs validation.

PR #79 merged as `99d9c2d985b8a21c62fe148e07e08b3632ef961a`.

### Docker release runtime through merged PR #80

- standalone release Compose without application bind mounts;
- production frontend Nginx image;
- internal PostgreSQL and Redis networking;
- frontend/backend health checks and same-origin API proxy;
- clean-environment image build and startup;
- API project creation, Alembic head, and restart-persistence checks;
- focused diagnostics and unconditional cleanup.

PR #80 passed exact-head Quality #454, Document Quality #84, Guided Release Acceptance #35, Operator Docs #21, and Docker Release Runtime #17 and merged as `939828e8c335966dde2d04c5083ee7d2da07c6eb`.

## IN PROGRESS

### Product completeness audit

- compare approved `PRODUCT_SPEC.md` areas with implemented behavior;
- identify release-blocking user and domain gaps;
- keep basic Alembic, PostgreSQL, backup/restore, Docker, and full Quality gates mandatory;
- move the final migration downgrade/re-upgrade cycle after feature freeze;
- record the Product Owner decision to implement System Settings before access foundation.

## NEXT — SYSTEM SETTINGS FOUNDATION

The next capability is a dedicated system-settings area. Detailed scope will be confirmed before implementation.

Expected boundaries:

- club name, logo, and branding continuity;
- site appearance customization;
- explicit typed settings for application modules;
- invitation-related policy and configuration;
- outbound mail configuration with protected secret handling;
- a Russian responsive administration page;
- defaults, validation, reset behavior, and change-impact rules.

Invitation delivery and user management must not be silently bundled into this slice unless explicitly approved after requirements clarification.

## FOLLOW-UP PRODUCT WORK

1. **Access foundation** — administrator bootstrap, invitation-only users, roles, authentication, guarded routes, and backend authorization.
2. **Recipe ownership and lifecycle** — CLUB/PERSONAL ownership, variants, publication, moderation, and generation modes.
3. **Central alcohol prohibition** — one backend policy across Product, Recipe, and CSV import paths.
4. **Actor-aware audit log** — safe history for project, menu, recipe, user, role, and settings changes.
5. **Consolidated export completeness** — approved Russian PDF and workbook contents using one brand snapshot.
6. **Product acceptance and feature freeze** — catalogue/import acceptance, optional-scope decisions, and end-to-end scenarios.

## FINAL RELEASE READINESS

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- production-like deployment checklist;
- final release workflow;
- release tag after green exact-head gates.

## LATER

- participant profiles, routes, logistics, and load distribution;
- warehouse balances, shops, prices, and price aggregation;
- broader preference modes beyond explicitly approved first-release behavior.

Multi-tenant support and microservices remain prohibited.
