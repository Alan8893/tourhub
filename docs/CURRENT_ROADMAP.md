# TourHub Current Roadmap

Status date: 2026-07-17

## Product goal

Deliver the approved local MVP for one tourist club without changing the approved architecture.

```text
Project preparation baseline
  → Production-like Docker runtime
  → Product completeness audit
  → Access and roles
  → Recipe ownership and lifecycle
  → Central domain safety
  → Actor-aware audit
  → Consolidated Russian exports
  → Product acceptance and feature freeze
  → Final migration and release gates
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

### Ready PR #80 — Docker release runtime validation

- standalone release Compose stack without application source bind mounts;
- production frontend Nginx image;
- internal PostgreSQL and Redis networking with the named database volume preserved;
- frontend/backend health checks and same-origin API proxying;
- disposable clean-environment image build and startup;
- app shell, API health, project creation, migration head, and restart-persistence checks;
- focused diagnostics and unconditional cleanup.

Exact head `73b233f7529d5d310a750071d592e9b108b9a1df` passed Quality #454, Document Quality #84, Guided Release Acceptance #35, Operator Docs #21, and Docker Release Runtime #17.

### Stacked draft PR #81 — product completeness audit

- compare every approved `PRODUCT_SPEC.md` area with implemented behavior;
- identify release-blocking user and domain gaps;
- keep PR #80 independent and mergeable;
- move final migration downgrade/re-upgrade smoke after first-release feature freeze;
- preserve basic Alembic, PostgreSQL, backup/restore, Docker, and full Quality gates throughout feature development;
- define the implementation order in `PRODUCT_COMPLETENESS_AUDIT.md`.

## NEXT — RELEASE-BLOCKING PRODUCT WORK

1. **Access foundation**
   - administrator bootstrap;
   - invitation-only users;
   - Administrator, Instructor, and Verified Instructor roles;
   - authentication, logout, guarded routes, and backend authorization.
2. **Recipe ownership and lifecycle**
   - CLUB and PERSONAL ownership;
   - multiple Recipe variants per Dish;
   - submission, review, approval, rejection comments, publication, and archive;
   - approved generation modes.
3. **Central alcohol prohibition**
   - one backend policy across Product, Recipe, and CSV import paths;
   - reviewed handling of existing prohibited records.
4. **Actor-aware audit log**
   - project, participant, menu, recipe, publication, user, and role changes;
   - safe metadata without passwords, tokens, or sensitive binary values.
5. **Consolidated export completeness**
   - approved complete Russian PDF;
   - workbook sheets `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование`;
   - one consistent brand snapshot across PDF, Excel, print, and ZIP.
6. **Product acceptance and feature freeze**
   - active deployment catalogue acceptance;
   - catalogue-import interaction coverage;
   - explicit Product Owner decisions for preference priority and optional recipe metadata;
   - role-based end-to-end browser acceptance.

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
