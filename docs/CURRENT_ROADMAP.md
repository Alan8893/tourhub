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
  → Copy Project from completed template (future explicit task)
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

### TH-0095 — Project workspace navigation

Compact routed Overview, Menu, Shopping, Equipment, and Documents work areas with responsive navigation and no horizontal overflow at accepted widths.

### TH-0097 — Product catalogue editing

Shared Product fields can be corrected without changing Product IDs, Recipe relationships, or RecipeComponent values.

### TH-0098 — Published Recipe Dish synchronization

Publication synchronizes the Recipe into Dishes in the publication transaction. Exact-name matches become variants; otherwise one role-less Dish is created. Generator roles remain explicitly human-owned.

### TH-0099 through TH-0103 — Semantic audit coverage

Project, Menu/MealSlot, System Settings/mail, invitation lifecycle/delivery, catalogue/import, shopping, equipment, and document-generation writes record bounded actor-attributed events at explicit transaction/result boundaries. No-op writes are suppressed and protected values are excluded.

### TH-0104 — Personal account and club contacts

- the header logout button is replaced by a responsive current-user control opening `/account`;
- `Личный кабинет` is available in the sidebar to every authenticated active user;
- existing `display_name` remains one FIO field and email remains read-only;
- optional phone, Telegram, MAX, and VK fields persist through Alembic head `h10022`;
- phone and social values are normalized by Backend, with platform hosts restricted to approved HTTPS URLs;
- Project-scoped contact cards expose email, `tel:`, Telegram/MAX/VK links, and downloadable vCard;
- password change verifies the current password, preserves the current login, and revokes all other active logins;
- profile and password actions append safe semantic audit events without contact values, passwords, hashes, cookies, or tokens;
- real-Chrome acceptance covers desktop/mobile layout, profile update, contacts, vCard, password change, navigation, and logout.

### TH-0105 — Project ownership, team access, and project contacts

- every Project has one owner and may have multiple additional instructors;
- Project visibility and direct routes are controlled by centralized `ProjectAccessPolicy`;
- completed Projects are hidden by default and remain terminal read-only history;
- team contacts are Project-scoped and ownership transfer is audited transactionally;
- current post-release Alembic head is `h10023`.

### TH-0106 — Audit CSV export

- one Administrator-only CSV export endpoint sits beside the existing Audit list;
- list and export reuse the same Backend-owned actor, entity, action, and date filters;
- only persisted sanitized AuditEvent snapshots are exported with deterministic UTF-8 JSON columns;
- spreadsheet formula cells are neutralized and exports are capped at 10,000 rows;
- the Audit surface exposes date filters and `Скачать CSV`;
- Backend, Frontend, and real-Chrome acceptance cover policy and UX;
- retention UI, deletion/cleanup, SIEM, diagnostics, scheduling, and replay remain out of scope;
- no migration was added, so current Alembic head remains `h10023`.

## Current post-release selection

### TH-0107 — Session administration and individual revocation

- every active authenticated user may list only their own active non-expired sessions;
- Backend identifies the current session from the existing HttpOnly cookie and never returns raw tokens or token hashes;
- one other owned session may be revoked individually;
- the current session remains protected and is terminated only through ordinary logout;
- revocation and safe `account_session_revoked` audit append share one transaction;
- `/account` shows session timestamps, current marker, revoke progress, success, and error feedback;
- Backend, Frontend, and real-Chrome acceptance cover ownership, immediate invalidation, rollback, and mobile layout;
- no migration is expected, so Alembic remains `h10023`.

Global sign-out, Administrator access to other users' sessions, device/IP tracking, physical cleanup, and account retention policy remain separate future work.

## Explicit future task — Copy Project

`Копировать проект` is a required later capability and must not be lost from planning. From a completed Project, the owner or an Administrator will start a new Project using the old Project as a template. The flow will reuse the normal new-Project parameter form for name, dates, duration, participant count, and meal boundaries, then copy the approved menu and preparation/settings structure into a new identity without reopening or mutating the completed source Project. Exact copied domains, historical attribution, recalculation rules, and notification behavior require a separate Product Owner-approved task before implementation.

## Deferred non-blocking priorities

### Audit and operations

- retention UI, external SIEM integration, and operational diagnostics;
- scheduled/background export delivery;
- undo and event replay remain outside v0.1.0.

### Access and identity

- verified email change and phone/email verification;
- account recovery, deletion, retention policy, and avatars;
- public member profiles, global sign-out, Administrator session administration, and session cleanup;
- invitation cleanup, asynchronous mail, bounce handling, and advanced templates.

### Product and operations

- richer Recipe metadata, per-meal switching, and preference weights;
- Product/Dish archive-management UI and ownership-aware import UX;
- trip-participant profiles, routes/GPX, warehouse, procurement, and external aggregation domains;
- scheduled/emailed documents, persisted versions, signatures, and encrypted configuration archives.

Multi-tenant support and microservices remain prohibited.
