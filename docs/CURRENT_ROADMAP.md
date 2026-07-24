# TourHub Current Roadmap

Status date: 2026-07-24

## Product goal

Operate the approved local ERP release for one tourist club without changing the modular-monolith architecture or accepted single-club boundary.

```text
First-release preparation and operations
  → System Settings and Access
  → Recipe ownership, moderation, Dish variants, and generation modes
  → Actor-aware audit foundation
  → complete Russian exports and central alcohol prohibition
  → Product acceptance, release readiness, and v0.1.0
  → Project workspace UX (TH-0095)
  → Product catalogue editing (TH-0097)
  → Published Recipe Dish synchronization (TH-0098)
  → Project audit coverage (TH-0099)
  → Menu generation and MealSlot audit coverage (TH-0100)
  → System Settings and mail audit coverage (TH-0101)
  → Invitation lifecycle and delivery-result audit coverage (TH-0102)
  → Catalogue/import, shopping, equipment, and document audit coverage (TH-0103)
  → Personal accounts and active club contacts (TH-0104)
  → Project ownership, team access, and project contacts (TH-0105)
  → Safe filtered audit CSV export (TH-0106)
  → Own session administration and individual revocation (TH-0107)
  → Product archive management (TH-0108)
  → Dish archive management (TH-0109)
  → Ownership-aware Recipe CSV import (TH-0110)
  → Copy Project from completed template (TH-0111)
  → next post-release task requires explicit selection
```

## Released first-release sequence

- complete guided preparation from Project creation through Menu, shopping, checklist, equipment, readiness, and Russian documents;
- production-like local Docker runtime, backup/restore, health checks, LAN access, and restart persistence;
- typed System Settings, invitation-only Access, users, roles, SMTP delivery, and multi-session readiness;
- CLUB/PERSONAL Recipe ownership, moderation, ordered Dish variants, generation modes, and persisted assignment Recipe snapshots;
- append-only actor-aware AuditEvent foundation through `h10020`;
- complete consolidated Project exports;
- centralized no-exceptions alcohol policy and released Alembic head `h10021`;
- machine-readable Product Acceptance and Release Readiness evidence;
- immutable `v0.1.0` release tag and backup-based production rollback boundary.

## Delivered post-release improvements

### TH-0095 through TH-0103

Responsive Project workspace navigation, Product editing, published Recipe-to-Dish synchronization, and semantic audit coverage across Project, Menu/MealSlot, System Settings/mail, invitations, catalogue/import, Shopping/Checklist, Equipment, and Documents are delivered.

### TH-0104 through TH-0107

Personal account/contact profiles, Project ownership and team-scoped access, safe filtered Audit CSV export, and own-session administration with individual revocation are delivered. Current post-release Alembic head is `h10023`.

### TH-0108 through TH-0110

Product and Dish archive management preserve history and policy lock while keeping active projections stable. Recipe CSV import supports actor/content/scope-bound CLUB/PERSONAL creation without changing Product CSV or legacy Recipe CLUB compatibility. These tasks required no migration.

### TH-0111 — Copy Project

- a completed Project may be copied only by its owner or an Administrator;
- the ordinary Project parameter form supplies editable destination values;
- the destination is a new actor-owned draft with a recreated MealSlot schedule;
- only matching assignments with currently usable Dish and Recipe dependencies are copied;
- skipped assignments are reported as bounded warnings;
- source identity, team, completion state, derived shopping/equipment/document state, and history remain unchanged;
- destination state and `project_copied` audit share one transaction;
- responsive UI and real-Chrome acceptance cover edited request mapping, duplicate submission protection, result navigation, warnings, source immutability, and mobile layout;
- no migration was required and Alembic remains `h10023`.

## Current post-release selection

No product task is active after TH-0111. Deferred items do not become active merely because they appear below.

## Deferred non-blocking priorities

### Audit and operations

- retention UI after duration, deletion eligibility, safeguards, and rollback policy are approved;
- external SIEM integration and operational diagnostics;
- scheduled/background export delivery;
- undo and event replay remain outside v0.1.0.

### Access and identity

- verified email change and phone/email verification;
- account recovery, deletion, retention policy, and avatars;
- public member profiles, global sign-out, Administrator session administration, and session cleanup;
- IP/device/user-agent/location tracking remains unapproved and unimplemented;
- invitation cleanup, asynchronous mail, bounce handling, and advanced templates.

### Product and operations

- Project-team notifications and reusable team templates;
- richer Recipe metadata, per-meal switching, and preference weights;
- trip-participant profiles, routes/GPX, warehouse, procurement, and external aggregation domains;
- scheduled/emailed documents, persisted versions, signatures, and encrypted configuration archives.

Multi-tenant support and microservices remain prohibited.
