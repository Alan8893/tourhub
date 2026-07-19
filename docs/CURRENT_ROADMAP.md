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
  → Project workspace UX (TH-0095)
  → Product catalogue editing (TH-0097)
  → Published Recipe Dish synchronization (TH-0098)
  → Project audit coverage (TH-0099)
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
- dedicated manifest, selected Backend API/migration, and critical Chrome scenarios;
- approved capabilities accepted and optional gaps explicitly deferred as non-blocking;
- first-release scope feature frozen at Alembic `h10021`.

### Final migration and release readiness — TH-0093 / PR #103

- machine-readable release contract for tag `v0.1.0`;
- real PostgreSQL 18 `h10020 → h10021 → h10020 → h10021` cycle with historical data;
- one Alembic head and final revision `h10021`;
- versioned deployment checklist, release notes, exact-head workflows, and backup-based rollback boundary;
- immutable tag lifecycle verified on later `main` pushes.

## DELIVERED POST-RELEASE IMPROVEMENTS

### Project workspace navigation and responsive layout — TH-0095 / PR #105

- compact Project Overview and stable Menu, Shopping, Equipment, and Documents routes;
- Project settings dialog and separate Shopping calculation/checklist views;
- temporary navigation drawer below desktop width;
- responsive acceptance at 360 px, 831 px, and 1280 px;
- no Backend, calculation, authorization, document, or Alembic change.

### Product catalogue editing — TH-0097 / PR #107

- active shared Products can be edited from the Recipe component workflow;
- name, category, catalogue unit, and package size retain central Backend validation;
- Product identifiers and Recipe relationships remain stable;
- RecipeComponent amount/unit values are never converted implicitly;
- focused Backend and real-Chrome acceptance cover the workflow without a migration.

### Published Recipe Dish synchronization — TH-0098 / PR #108

- Recipe publication and Dish synchronization use one transaction and rollback boundary;
- an already attached Recipe is never duplicated;
- an active exact-name Dish receives the Recipe as the next variant while keeping its default and roles;
- otherwise publication creates one active Dish with the Recipe as default and only variant;
- publication-created Dishes remain unclassified and available for manual selection;
- the Dish catalogue shows `Не настроено для генератора` until explicit roles are assigned;
- `Настроить генератор` opens the existing role editor;
- configured Dishes show `Готово для генератора` and contribute to readiness coverage;
- no role, meal type, or repeatability value is inferred;
- strict Ruff/mypy, full Backend regression, Product Acceptance Chrome, and responsive focused Chrome coverage verify the behavior;
- Alembic remains `h10021`.

### Project audit coverage — TH-0099 / PR #109

- `project_created` is recorded with the authenticated actor in the Project creation commit;
- `project_participants_updated` shares the participant and derived-data recalculation transaction;
- `project_generation_mode_updated` shares the Project update commit;
- `project_prepared` shares one caller-owned transaction with purchase list, checklist, and equipment preparation;
- no-op participant and generation-mode updates do not create events;
- failures roll back both domain changes and pending AuditEvents;
- standalone preparation services retain commit-by-default behavior;
- the Administrator Audit surface exposes Russian Project labels and filters;
- focused success/no-op/attribution/rollback tests, strict Ruff/mypy, all Backend tests, Product Acceptance, and real-Chrome Audit coverage verify the behavior;
- no migration, architecture change, new Project capability, or release-tag movement occurred.

## NEXT POST-RELEASE SELECTION

No task after TH-0099 is selected automatically. Menu generation/manual MealSlot auditing remains the next listed audit debt, but work requires a separate Product Owner decision.

## Deferred non-blocking priorities

### Audit coverage

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
