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
  → Final migration and release gates
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

## NEXT

1. **Product Acceptance and Feature Freeze** — run approved end-to-end catalogue/import/access/preparation/export scenarios, classify remaining gaps, and explicitly freeze or defer optional scope.

## Audit coverage still required

The shared foundation is implemented, but later explicit instrumentation remains for project/menu edits, settings, mail, invitations, catalogue/import, shopping, equipment, and document-generation actions. Automatic ORM-wide auditing remains rejected.

## Deferred operations

- session administration, cleanup, global sign-out, and account recovery;
- asynchronous mail queues, scheduled retries, and delivery diagnostics beyond the current synchronous result;
- moderation notifications;
- per-meal manual Recipe switching and preference weights beyond the approved three project modes;
- audit export, retention UI, SIEM integration, undo, and event replay;
- scheduled or emailed document generation and document-download audit events;
- Product/Dish archive-management UI;
- fuzzy/external alcohol classification and user-configurable exceptions;
- additional same-origin request hardening if deployment expands beyond trusted LAN;
- external identity providers and MFA.

## Final release readiness

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- production-like deployment checklist;
- final release workflow and release tag after green exact-head gates.

Multi-tenant support and microservices remain prohibited.
