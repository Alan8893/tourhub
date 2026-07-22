# TourHub Current Roadmap

Status date: 2026-07-22

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
  → next post-release task requires explicit selection
  → Copy Project from completed template remains required future work
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

### TH-0104 — Personal account and club contacts

- `/account` contains editable profile fields, read-only email, password change, and logout;
- optional phone, Telegram, MAX, and VK fields persist through `h10022`;
- Project-scoped contact cards expose approved actions and vCard;
- password change preserves the current login and revokes all other active logins;
- profile and password actions append safe semantic audit events.

### TH-0105 — Project ownership, team access, and project contacts

- every Project has one owner and may have multiple additional instructors;
- Project visibility and direct routes are controlled by centralized `ProjectAccessPolicy`;
- completed Projects are hidden by default and remain terminal read-only history;
- team contacts are Project-scoped and ownership transfer is audited transactionally;
- current post-release Alembic head is `h10023`.

### TH-0106 — Audit CSV export

- one Administrator-only CSV export endpoint sits beside the existing Audit list;
- list and export reuse the same Backend-owned filters;
- only persisted sanitized AuditEvent snapshots are exported with deterministic UTF-8 JSON columns;
- spreadsheet formula cells are neutralized and exports are capped at 10,000 rows;
- no migration was added, so current Alembic head remains `h10023`.

### TH-0107 — Session administration and individual revocation

- every active authenticated user can list only their own active non-expired sessions;
- Backend identifies the current login from the existing HttpOnly cookie without returning token material;
- one other owned active session can be revoked individually;
- current-session revocation is blocked and ordinary logout remains its termination path;
- revocation and `account_session_revoked` share one transaction;
- no migration was required, so Alembic remains `h10023`.

### TH-0108 — Product archive management

- preparation users can soft-archive an active Product and restore a manually archived Product;
- the normal Product list and Recipe component selector remain active-only;
- archived Products are visible only through an explicit protected archive-management read;
- Product rows and historical Recipe, purchase, checklist, and document references are preserved;
- policy-locked Products cannot be restored, and restore re-runs the central alcohol policy;
- archive/restore are row-locked, idempotent, and audited transactionally;
- existing Recipe/Product contracts remain stable through separate archive DTOs;
- responsive Frontend and real-Chrome acceptance cover the lifecycle;
- no migration was required, so Alembic remains `h10023`.

### TH-0109 — Dish archive management

- the normal Dish catalogue and new Dish selection remain active-only with the stable `DishResponse` contract;
- an explicit protected archive projection exposes archived Dish identity, recipe display data, and policy-lock state;
- preparation users can soft-archive one Dish and restore a manually archived Dish;
- Dish rows, Recipe variants, meal-role assignments, and historical MealSlot/project references are preserved;
- restore re-runs the central Dish-name alcohol policy and policy-locked Dishes remain non-restorable;
- archive/restore use row locks, idempotency, and transactional `dish_archived` / `dish_restored` events;
- responsive active/archive UI and real-Chrome acceptance cover state transitions, policy lock, and mobile overflow;
- existing Dish archive columns were reused, so Alembic remains `h10023`.

## Current post-release selection

No product task is active after TH-0109. Deferred items do not become active merely because they appear below.

## Explicit future task — Copy Project

`Копировать проект` is a required later capability and must not be lost from planning. From a completed Project, the owner or an Administrator will start a new Project using the old Project as a template. The flow will reuse the normal new-Project parameter form for name, dates, duration, participant count, and meal boundaries, then copy the approved menu and preparation/settings structure into a new identity without reopening or mutating the completed source Project. Exact copied domains, historical attribution, recalculation rules, and notification behavior require a separate Product Owner-approved task before implementation.

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

- ownership-aware CSV import UX;
- richer Recipe metadata, per-meal switching, and preference weights;
- trip-participant profiles, routes/GPX, warehouse, procurement, and external aggregation domains;
- scheduled/emailed documents, persisted versions, signatures, and encrypted configuration archives.

Multi-tenant support and microservices remain prohibited.
