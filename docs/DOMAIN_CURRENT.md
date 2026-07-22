# TourHub Current Domain Model

Status: Active

Last updated: 2026-07-22

## Purpose

This document describes the implemented domain baseline. `PRODUCT_SPEC.md` describes approved target scope. Deferred capabilities are not current implementation.

## Club, identity, and access

One installation represents one tourist club. Multi-tenant support is prohibited.

Implemented identity model:

- one-time bootstrap creates the first active Administrator;
- later users are created only by accepting Administrator-issued one-time invitations;
- one User has one global role: `administrator`, `instructor`, or `verified_instructor`;
- one User may own multiple independent server sessions;
- raw session and invitation values are never persisted;
- active state is checked on every authorized request;
- deactivation revokes sessions and removes runtime Project access;
- at least one active Administrator must always remain;
- user/profile updates use optimistic versions.

A User owns one editable personal contact profile with one FIO field, read-only login email, optional phone/Telegram/MAX/VK, role, active state, and version. Profile contact values are exposed to another user only through shared access to a Project team.

Only an active Administrator may read or export the club-wide AuditEvent journal.

## AuthSession and own-session projection — TH-0107

`AuthSession` remains the persisted authentication boundary:

```text
AuthSession
  ├─ id
  ├─ user_id → User
  ├─ token_hash
  ├─ created_at
  ├─ last_seen_at
  ├─ expires_at
  └─ revoked_at?
```

The personal-account projection exposes only:

```text
AccountSession
  ├─ id
  ├─ created_at
  ├─ last_seen_at
  ├─ expires_at
  └─ is_current
```

Rules:

- an active authenticated User receives only their own rows with no revocation timestamp and future expiry;
- the current login is matched by hashing the existing HttpOnly cookie in Backend;
- raw tokens, token hashes, cookies, authorization headers, IP, user-agent, device, fingerprint, and location are not projection fields;
- another owned active session may be revoked by ID;
- unrelated, revoked, expired, and unknown session IDs are indistinguishable as not found;
- the current login cannot be revoked through this operation and remains controlled by logout;
- individual revocation updates `revoked_at` and appends `account_session_revoked` in one transaction;
- audit context is `current_login_preserved`, deliberately avoiding sanitizer-sensitive `session`, `token`, and `cookie` keys;
- global sign-out, cross-user Administrator session management, cleanup, and physical deletion remain future capabilities.

## Project ownership and team

```text
Project
  ├─ owner_user_id → User
  ├─ ProjectInstructor[]
  ├─ name, participants, days, start_date
  ├─ first_meal, last_meal
  ├─ recipe_generation_mode
  ├─ status
  └─ preparation results

ProjectInstructor
  ├─ project_id → Project
  ├─ user_id → User
  ├─ added_by_user_id → User?
  └─ created_at
```

Rules:

- every newly created Project belongs to the creating active user;
- production Projects have exactly one owner and any number of additional instructors;
- owner and additional-instructor membership are mutually exclusive;
- Administrators may be additional instructors without changing their global role;
- inactive users retain historical ownership/membership but cannot access the Project;
- existing owners are backfilled by `h10023` from the earliest trustworthy `project_created` AuditEvent, with first-Administrator fallback.

An active User may view a Project when they are an Administrator, owner, or additional instructor. An unrelated User receives no catalogue item and HTTP 404 for direct or nested Project access.

Owner or Administrator may manage Project parameters, Menu, preparation, team, ownership, completion, deletion, and every operational module while open. Additional instructors may view Project/Menu and operate Shopping, Checklist, Equipment, Documents, and contacts, but may not write Menu or Project/team/settings/status/deletion state.

Ownership transfer removes the new owner from additional membership, retains the previous owner as an additional instructor, changes ownership, and records one semantic event in one transaction.

`completed` is terminal. Completed Projects are hidden by default, remain readable/downloadable to authorized users, reject operational writes, may be deleted by owner/Administrator, and cannot be reopened. Future `Копировать проект` creates a new identity and is not implemented.

## Project team contacts

Project team projection contains the owner first and additional instructors in deterministic order, with global role, Project role, active state, and contact profile fields. Active authorized team viewers receive approved mail/phone/social/vCard actions; inactive historical members remain identifiable but have no contact actions. The former club-wide `/account/contacts` directory is removed.

`ProjectTeamNotificationService` remains a no-op boundary. No mail, Telegram, MAX, queue, retry, provider message, or delivery history is created.

## AuditEvent

AuditEvent is append-only and stores actor snapshots, semantic action, entity identity, safe before/after/context JSON, and timestamp.

Current personal-account actions include:

- `account_profile_updated`;
- `account_password_changed`;
- `account_session_revoked`.

For individual session revocation, `entity_type` is `auth_session`, entity ID is the target session ID, before/after contain only active/revoked state, and context contains only `current_login_preserved`. Token values, hashes, cookies, authorization headers, IP/device data, and user-agent strings are excluded.

Team, ownership, completion, deletion, personal-account writes, and their AuditEvents share owning transactions. No-op writes create no event. Audit failure rolls back pending domain mutation. Automatic ORM-wide auditing remains rejected.

### Audit CSV projection — TH-0106

The CSV export is a read projection over existing AuditEvent rows, not a new persisted entity.

```text
AuditCsvRow
  ├─ id, created_at
  ├─ actor_user_id?, actor_display_name, actor_email, actor_role
  ├─ action
  ├─ entity_type, entity_id?
  ├─ before_json?
  ├─ after_json?
  └─ context_json
```

Rules:

- only an active Administrator may request the projection;
- actor user ID, entity type, entity ID, action, created-from, and created-to filters have the same Backend semantics as the Audit list;
- JSON columns serialize only already-sanitized persisted mappings with deterministic key ordering;
- UTF-8 BOM supports Russian spreadsheet applications and formula-like text is neutralized;
- at most 10,000 matching rows may be exported in one request;
- export does not create an AuditEvent or alter domain state;
- retention deletion/cleanup, retention UI, SIEM delivery, diagnostics, scheduling, undo, and replay are not part of this projection.

## Menu, catalogue, documents, and mail

MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only. MealSlotDish persists the exact selected Recipe. Project Recipe generation modes remain `club_only`, `club_and_personal`, and `personal_preferred`.

Product, Recipe ownership/lifecycle, Dish Recipe variants, exact assignment snapshots, archive state, and the central no-exceptions alcohol policy remain unchanged. Archived records remain readable historically and are excluded from new active use.

Consolidated Project documents remain non-persisted immutable snapshots. Authorized Project members may generate/download approved documents; completed Projects retain document access as read-only history. Audit stores only safe document metadata.

MailSettings and invitation delivery retain existing boundaries. Project-team notifications are not connected to mail or messaging providers.

## Current migrations

- released `v0.1.0`: `h10021`;
- optional User contact profile: `h10022`;
- Project owner/team membership: `h10023` current head;
- TH-0106 Audit CSV export: no migration;
- TH-0107 Session Administration: no migration.

## Future domains and tasks

- copy a completed Project into a new Project template instance;
- audit retention policy/UI after required Product Owner decisions;
- global sign-out, Administrator session administration, and session cleanup;
- Product/Dish archive-management UI and ownership-aware CSV import UX;
- Project-team notifications through email, Telegram, and MAX;
- participant profiles, routes/GPX, logistics, warehouse, and procurement integrations.

No post-release product task is active after TH-0107. Multi-tenant support remains prohibited.
