# TourHub Current Roadmap

Status date: 2026-07-17

## Product goal

Deliver the approved local MVP for one tourist club without changing the approved architecture.

```text
Project preparation baseline
  → Production-like Docker runtime
  → Product completeness audit
  → System Settings foundation
      → Club profile and settings shell
      → Site appearance
      → Document appearance
      → Module visibility and dependency locks
      → Future invitation/mail configuration boundaries
  → Access and roles
  → Working mail delivery
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
- project creation, role-aware menu generation, and authoritative manual editing;
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

PR #80 merged as `939828e8c335966dde2d04c5083ee7d2da07c6eb`.

### Product completeness audit through merged PR #83

- compared the approved product specification with implemented behavior;
- separated implemented, partial, missing, future, and Product Owner decision items;
- kept basic Alembic, PostgreSQL, backup/restore, Docker, and full Quality gates mandatory;
- moved the final migration downgrade/re-upgrade cycle after feature freeze;
- recorded System Settings as the next capability before access foundation.

PR #83 merged as `950a43914230f6fe4be3bf217a4e5f1b79e7265f`.

### System Settings club foundation through merged PR #84

- dedicated responsive `/settings` page and main-sidebar entry;
- typed singleton club profile with optional identity/contact/location fields and approved images;
- PNG/JPEG/WebP validation with no SVG;
- optimistic versioning, PostgreSQL row locking, HTTP 409 conflicts, and safe history;
- legacy `/club-settings` compatibility and additive Alembic `h10008`.

PR #84 merged as `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a`.

### System Settings site appearance through merged PR #85

- independently typed singleton `AppearanceSettings` and Alembic `h10009`;
- organization-wide light/dark tokens, safe presets, fonts, density, shape, and component styles;
- backend contrast validation with Russian reasons;
- global dynamic MUI theme and per-browser display mode;
- isolated preview, reset, cancel, copy, validated JSON import, and JSON export.

PR #85 merged as `0e4e376470072e9475a31504faeb46e8b5a68364`.

### System Settings document appearance through merged PR #86

- independently typed singleton `DocumentAppearanceSettings` and Alembic `h10010`;
- document palette, logo selection, contacts, footer, title image, and table density;
- backend contrast validation and versioned safe history;
- one frozen club/document snapshot per generation request;
- the same snapshot reused by purchase/equipment PDF, Excel, print, and every ZIP entry;
- responsive editor and isolated document preview;
- existing routes, filenames, content types, and legacy branding compatibility preserved.

PR #86 passed exact-head Quality #575, Document Quality #201, Guided Release Acceptance #152, Operator Docs #138, and Docker Release Runtime #133 and merged as `18d5c9637e2e692b630009167dd622ee40ee2747`.

## IN PROGRESS — TH-0077 / DRAFT PR #87

### System Settings: module visibility and dependency locks

- independent singleton `ModuleSettings` with explicit typed boolean columns;
- required visible `Проекты` and `Каталог` modules;
- optional `Импорт`, `Закупка`, `Оборудование`, and `Документы` visibility;
- visible documents require visible shopping and equipment;
- backend dependency validation, PostgreSQL row locking, HTTP 409 conflicts, and safe history;
- desktop/mobile sidebar visibility updates without restart;
- shopping, equipment, and document project cards follow the saved visibility snapshot;
- direct URLs and APIs remain available;
- additive Alembic `h10011` with one head.

Scope boundary:

- visibility is not authorization;
- routes, APIs, and backend domain modules are not disabled;
- settings and required modules remain visible;
- invitation policy, functional invitations, users, roles, authentication, and SMTP remain separate.

## NEXT — REMAINING SYSTEM SETTINGS BOUNDARIES

1. **Future invitation configuration**
   - typed policy fields before users exist;
   - no functional invitation list until access foundation.
2. **Informative mail boundary**
   - explain the future universal SMTP contract and write-only secret boundary;
   - no working delivery until identity exists.

## FOLLOW-UP PRODUCT WORK

1. **Access foundation** — administrator bootstrap, invitation-only users, roles, authentication, guarded routes, and backend authorization.
2. **Working mail delivery** — universal SMTP, environment/write-only password, sender identity, test address, retries, status, and fixed Russian test template.
3. **Recipe ownership and lifecycle** — CLUB/PERSONAL ownership, variants, publication, moderation, and generation modes.
4. **Central alcohol prohibition** — one backend policy across Product, Recipe, and CSV import paths.
5. **Actor-aware audit log** — safe history for project, menu, recipe, user, role, mail, and settings changes.
6. **Consolidated export completeness** — approved Russian PDF and workbook contents using one brand snapshot.
7. **Product acceptance and feature freeze** — catalogue/import acceptance, optional-scope decisions, and end-to-end scenarios.

## FINAL RELEASE READINESS

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- production-like deployment checklist;
- final release workflow;
- release tag after green exact-head gates.

## LATER

- participant profiles, routes, logistics, and load distribution;
- warehouse balances, shops, prices, and price aggregation;
- broader preference modes beyond explicitly approved first-release behavior;
- organization-provided custom CSS;
- full visual reference matching from uploaded examples.

Multi-tenant support and microservices remain prohibited.