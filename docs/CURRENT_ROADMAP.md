# TourHub Current Roadmap

Status date: 2026-07-19

## Product goal

Deliver and operate the approved local ERP release for one tourist club without changing the modular-monolith architecture or the accepted single-club product boundary.

```text
Project preparation baseline
  → Production-like Docker runtime
  → Product completeness audit
  → System Settings foundation
  → Access foundation
  → Working mail delivery
  → Multi-user operational readiness
  → Recipe ownership foundation
  → Recipe publication and moderation
  → Dish recipe variants and generation modes
  → Actor-aware audit foundation
  → Consolidated Russian exports
  → Central alcohol prohibition
  → Product acceptance and feature freeze
  → Final migration and release readiness
  → v0.1.0
```

## RELEASED FIRST-RELEASE SEQUENCE

### Infrastructure, preparation, and operations

- complete guided preparation from Project creation through shopping, equipment, readiness, and Russian documents;
- installation, update, backup, restore, recovery, production-like images, health checks, same-origin API proxy, restart persistence, LAN access, and cleanup validation;
- PostgreSQL 18 and Redis remain internal to the release network.

### System Settings, Access, and mail — PR #84 through PR #95

- typed settings owners and responsive `/settings` surface (`h10008`–`h10013`);
- Administrator bootstrap, sessions, invitations, users, roles, and preparation authorization (`h10014`–`h10016`);
- working SMTP delivery with manual invitation-link fallback;
- multiple sessions, immediate role propagation, deactivation revocation, protected-401 handling, exact route return, and visible current role.

### Recipe ownership, moderation, and Dish variants — TH-0086 through TH-0088

- CLUB/PERSONAL ownership and nested authorization (`h10017`);
- lifecycle `draft`, `submitted`, `rejected`, and `published` with row-locked moderation (`h10018`);
- ordered Dish Recipe variants with one published CLUB default (`h10019`);
- three Project generation modes, private PERSONAL variants, deterministic rotation, persisted assignment Recipe snapshots, and assignment-based shopping/equipment calculations.

### Actor-aware audit foundation — TH-0089 / PR #99

- append-only `AuditEvent` persistence and migration `h10020`;
- actor identity snapshots, bounded secret filtering, semantic user-access and Recipe moderation events;
- immutable moderation history, Administrator filtering, and responsive Audit UI.

### Consolidated Russian exports — TH-0090 / PR #100

- complete Project PDF and workbook sheets `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование`;
- persisted assignment Recipes, purchasing/checklist state, equipment, warnings, comments, and one immutable branding snapshot;
- complete downloads plus compatibility endpoints and ZIP artifacts.

### Central alcohol prohibition — TH-0091 / PR #101

- one normalized complete-word Backend policy for Russian/English alcohol terms;
- one HTTP 422 boundary across Product, Recipe, Dish, Recipe lifecycle, and Product/Recipe CSV preview/apply;
- migration `h10021` archives existing prohibited Products, Recipes, and default Dishes while retaining historical relationships;
- policy markers distinguish automatic archival and prevent Recipe restore;
- false-positive boundaries such as `ромашка`, `пивные дрожжи`, and `винный уксус` remain allowed.

### Product acceptance and feature freeze — TH-0092 / PR #102

- machine-readable accepted release-scope manifest with evidence and architecture guards;
- dedicated manifest, selected Backend API/migration, and six critical Chrome scenarios;
- approved capabilities accepted and optional gaps explicitly deferred as non-blocking;
- first-release scope feature frozen at Alembic `h10021`.

### Final migration and release readiness — TH-0093 / PR #103

- machine-readable release contract for tag `v0.1.0`;
- real PostgreSQL 18 `h10020 → h10021 → h10020 → h10021` cycle with allowed, prohibited, manually archived, non-default variant, and historical assignment data;
- one Alembic head and final revision `h10021`;
- versioned deployment checklist, release notes, and backup-based rollback boundary;
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, and Docker Release Runtime on pushes to `main`;
- exact-head final workflow that creates lightweight tag `v0.1.0` only after every required merged-SHA workflow succeeds.

## POST-RELEASE SELECTION

No next product capability is selected automatically. The Product Owner must choose a separate post-release task from the documented debt or approve a new priority. The v0.1.0 release baseline remains unchanged until that decision.

## Deferred non-blocking priorities

### Audit coverage

- project creation/update/preparation;
- menu generation and manual MealSlot changes;
- System Settings, mail, invitations, catalogue/import, shopping, equipment, and document-generation writes;
- audit export, retention UI, SIEM, undo, and replay.

### Product and operations

- participant profiles, routes/GPX, warehouse balances, issue workflow, participant distribution, procurement prices, shops, stock balances, and external aggregators;
- session administration, account recovery, user profiles, asynchronous mail, bounce handling, advanced templates, and attachments;
- moderation notifications, richer Recipe metadata, per-meal Recipe switching, and preference weights;
- scheduled/emailed documents, signatures, Product/Dish archive-management UI, and encrypted configuration archives;
- additional same-origin request hardening only if deployment expands beyond the trusted-LAN model;
- external identity providers and MFA.

Multi-tenant support and microservices remain prohibited.
