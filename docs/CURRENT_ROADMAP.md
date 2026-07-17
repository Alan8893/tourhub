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
      → Module and future invitation/mail boundaries
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

PR #80 passed exact-head Quality #454, Document Quality #84, Guided Release Acceptance #35, Operator Docs #21, and Docker Release Runtime #17 and merged as `939828e8c335966dde2d04c5083ee7d2da07c6eb`.

### Product completeness audit through merged PR #83

- compared the approved product specification with implemented behavior;
- separated implemented, partial, missing, future, and Product Owner decision items;
- kept basic Alembic, PostgreSQL, backup/restore, Docker, and full Quality gates mandatory;
- moved the final migration downgrade/re-upgrade cycle after feature freeze;
- recorded System Settings as the next capability before access foundation.

PR #83 passed exact-head Quality #464, Document Quality #93, Guided Release Acceptance #44, Operator Docs #30, and Docker Release Runtime #25 and merged as `950a43914230f6fe4be3bf217a4e5f1b79e7265f`.

## IN PROGRESS — TH-0074 / DRAFT PR #84

### System Settings: shell and club profile

- dedicated responsive `/settings` page and main-sidebar entry;
- vertical section navigation on desktop and section selector on mobile;
- existing club settings moved out of the project workspace;
- typed singleton club profile with the club name as the only required value;
- optional short/legal name, description, address, phone, email, website, timezone, city, region, and labelled social links;
- main/light/dark logos, square icon, favicon, login background, and document image;
- PNG/JPEG/WebP validation with per-kind limits and no SVG;
- version-based stale-update protection with HTTP 409;
- safe local-administrator settings history with the latest 200 records;
- legacy `/club-settings` compatibility and unchanged existing document branding;
- additive Alembic revision `h10008` with one head.

Scope boundary:

- appearance design tokens and live preview remain the next settings slice;
- document appearance remains separate;
- module visibility and invitation/mail configuration boundaries remain separate;
- functional users, invitations, authentication, and mail delivery are not included;
- encrypted configuration archives require a dedicated security design.

## NEXT — REMAINING SYSTEM SETTINGS SLICES

1. **Site appearance**
   - validated light and dark design tokens;
   - organization-wide colors, typography, density, shape, and component styling;
   - personal light/dark/system mode in local storage until users exist;
   - isolated preview first, optional whole-application preview after stabilization;
   - defaults, reset, contrast explanations, and theme import/export without secrets.
2. **Document appearance**
   - independent document palette, title/table styles, footer, contacts, title background, and table density;
   - one immutable branded snapshot shared by PDF, Excel, print, and ZIP.
3. **Modules and future access configuration**
   - navigation visibility only in the first module slice;
   - required-module dependency locks enforced by the backend;
   - invitation policy fields without a functional invitation list;
   - informative mail section until access foundation exists;
   - direct URLs and APIs remain available while a module is hidden.

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
