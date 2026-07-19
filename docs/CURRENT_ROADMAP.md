# TourHub Current Roadmap

Status date: 2026-07-19

## Product goal

Deliver the approved local MVP for one tourist club without changing the approved modular-monolith architecture.

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
```

## DONE

### Infrastructure, preparation, and operations

- complete guided preparation from project creation through shopping, equipment, readiness, and Russian documents;
- installation, update, backup, restore, recovery, production-like release images, health checks, same-origin API proxy, restart persistence, and cleanup validation;
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
- project modes `club_only`, `club_and_personal`, and `personal_preferred`;
- private PERSONAL variants, deterministic rotation, persisted assignment Recipe snapshots, and assignment-based shopping/equipment calculations.

### Actor-aware audit foundation — TH-0089 / PR #99

- append-only `AuditEvent` persistence and migration `h10020`;
- actor identity snapshots, bounded secret filtering, semantic user-access and Recipe moderation events;
- immutable moderation history, Administrator filtering, and responsive Audit UI.

### Consolidated Russian exports — TH-0090 / PR #100

- one complete Project PDF and one workbook with sheets `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование`;
- persisted assignment Recipe snapshots, purchasing/checklist state, equipment, warnings, comments, and one immutable branding snapshot;
- complete downloads plus preserved compatibility endpoints and ZIP artifacts.

### Central alcohol prohibition — TH-0091 / PR #101

- one normalized complete-word Backend policy for Russian/English alcohol terms;
- one HTTP 422 boundary across Product, Recipe, Dish, Recipe lifecycle, and Product/Recipe CSV preview/apply;
- archive filtering for active Product/Dish catalogues and preparation selection;
- migration `h10021` archives existing prohibited Products, Recipes, and default Dishes while retaining historical foreign-key relationships;
- policy markers distinguish automatic archival and prevent Recipe restore;
- false-positive boundaries such as `ромашка`, `пивные дрожжи`, and `винный уксус` remain allowed.

### Product acceptance and feature freeze — TH-0092 / PR #102

- one machine-readable accepted release-scope manifest with evidence and architecture guards;
- one dedicated workflow covering manifest validation, selected real Backend API/migration scenarios, and six critical Chrome scenarios;
- approved first-release capabilities accepted and optional gaps explicitly deferred as non-blocking;
- feature freeze activated at Alembic head `h10021`;
- first-release scope changes limited to acceptance defects, security fixes, final release-readiness work, and documentation corrections.

## NEXT

1. **Final Migration and Release Readiness** — run the PostgreSQL previous → `h10021` → previous → `h10021` cycle, verify the production deployment checklist, add the final release workflow, and create the release tag only after green exact-head gates.

## Audit coverage deferred beyond the first release

The shared foundation is implemented, but later explicit instrumentation remains for project/menu edits, settings, mail, invitations, catalogue/import, shopping, equipment, and document-generation actions. Automatic ORM-wide auditing remains rejected.

## Other deferred non-blocking scope

- participant profiles, routes/GPX, warehouse balances, issue workflow, and participant distribution;
- procurement prices, shops, stock balances, and external aggregators;
- session administration, cleanup, global sign-out, account recovery, and user profile editing;
- asynchronous mail queues, scheduled retries, bounce handling, and advanced templates/attachments;
- moderation notifications;
- richer Recipe metadata, per-meal manual Recipe switching, and preference weights beyond the approved generation modes;
- audit export, retention UI, SIEM integration, undo, and event replay;
- scheduled or emailed document generation, signatures, and document-download audit events;
- Product/Dish archive-management UI;
- encrypted configuration archives;
- fuzzy/external alcohol classification and user-configurable exceptions;
- additional same-origin request hardening if deployment expands beyond trusted LAN;
- external identity providers and MFA.

Multi-tenant support and microservices remain prohibited.
