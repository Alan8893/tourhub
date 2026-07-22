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

A User owns one editable personal contact profile:

```text
User
  ├─ display_name: one FIO field
  ├─ email: unique login, read-only in personal account
  ├─ phone?
  ├─ telegram_url?
  ├─ max_url?
  ├─ vk_url?
  ├─ role
  ├─ is_active
  └─ version
```

Profile contact values are private from unauthenticated users and are exposed to another user only through shared access to a Project team. Account recovery, verified contact changes, deletion, avatars, public profiles, and general session administration remain future capabilities.

## Project ownership and team

Project is the preparation root for one trip.

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
- production Projects have exactly one owner;
- a Project may have any number of additional instructors;
- owner and additional-instructor membership are mutually exclusive;
- Administrators may be additional instructors without changing their global role;
- inactive users retain historical ownership/membership but cannot access the Project;
- reactivation restores access from the retained relationship;
- existing owners are backfilled by `h10023` from the earliest trustworthy `project_created` AuditEvent, with first-Administrator fallback.

### Visibility

An active User may view a Project when at least one condition is true:

- the User is an Administrator;
- the User is the owner;
- the User is an additional instructor.

An unrelated User receives no catalogue item and HTTP 404 for direct or nested Project access.

### Capabilities

Owner or Administrator, while the Project is open:

- change Project parameters and recipe-generation mode;
- generate/regenerate and manually edit Menu;
- run full preparation;
- operate Shopping, Checklist, Equipment, Documents, and contacts;
- manage additional instructors;
- transfer ownership;
- complete or delete the Project.

Additional instructor, while the Project is open:

- view Project and Menu;
- operate Shopping, Checklist, Equipment, Documents, and contacts;
- cannot write Menu or Project/team/settings/status/deletion state.

### Ownership transfer

A new owner may be any active supported User. Transfer removes the new owner from additional membership, retains the previous owner as an additional instructor, changes ownership, and records one semantic event in one transaction.

### Completion

`completed` is terminal. A completed Project:

- is hidden from the catalogue by default;
- remains visible to authorized users when completed items are requested;
- is read-only across Menu, settings, team, preparation, Shopping, Checklist, and Equipment;
- retains document reads/downloads;
- may be deleted by owner or Administrator;
- cannot be reopened.

Future `Копировать проект` will create a new Project identity from a completed template. It is not implemented.

## Project team contacts

Project team projection contains:

- the owner first;
- additional instructors ordered deterministically;
- global role, Project role, active state, and contact profile fields.

Active authorized team viewers receive mail, `tel:`, Telegram, MAX, VK, and Project-scoped vCard actions. Inactive historical members remain identifiable but contact actions are unavailable. Administrators who are not explicitly owner/team members are not listed as contacts even though they may view the Project.

The former club-wide `/account/contacts` directory is removed.

## Project-team notification boundary

`ProjectTeamNotificationService` defines callbacks for instructor add/remove and ownership transfer. The current implementation is no-op. No mail, Telegram, MAX, queue, retry, provider message, or delivery history is created.

## AuditEvent

AuditEvent is append-only and stores actor snapshots, semantic action, entity identity, safe before/after/context JSON, and timestamp.

Current Project-team actions include:

- `project_instructor_added`;
- `project_instructor_removed`;
- `project_owner_transferred`;
- `project_status_updated`;
- `project_deleted`.

Team, ownership, completion, deletion, and their AuditEvents share owning transactions. No-op membership/ownership writes create no event. Audit failure rolls back pending domain mutation.

Project-team payloads may include Project/User IDs, display names, global/project roles, and state metadata. Phone numbers, social URLs, passwords, hashes, sessions, tokens, credentials, request bodies, and provider details are excluded.

Existing audit coverage for user access, Recipe lifecycle, Project preparation, Menu/MealSlot, System Settings/mail, invitations, catalogue/import, Shopping/Checklist, Equipment, and Documents remains implemented. Automatic ORM-wide auditing remains rejected.

## Menu and preparation

MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only. MealSlotDish persists the exact selected Recipe.

Supported Project Recipe generation modes remain:

- `club_only`;
- `club_and_personal`;
- `personal_preferred`.

Owner/Administrator may generate and edit Menu. Additional instructors receive read-only Menu projection. Full preparation is owner/Administrator-only because it may create or change Menu and downstream state.

Shopping/Checklist and Equipment operational writes are available to additional instructors while the Project is open. All Project-scoped routes apply central visibility and completion checks.

## Product, Recipe, Dish, and alcohol policy

Product, Recipe ownership/lifecycle, Dish Recipe variants, exact assignment snapshots, archive state, and the central no-exceptions alcohol policy remain unchanged. Archived records remain readable historically and are excluded from new active use.

## Documents and mail

Consolidated Project documents remain non-persisted immutable snapshots. Authorized Project members may generate/download approved documents; completed Projects retain document access as read-only history. Audit stores only safe document metadata.

MailSettings and invitation delivery retain existing boundaries. Project-team notifications are not yet connected to mail or messaging providers.

## Current migrations

- released `v0.1.0`: `h10021`;
- optional User contact profile: `h10022`;
- Project owner/team membership: `h10023` current head.

## Future domains

- copy a completed Project into a new Project template instance;
- Project-team notifications through email, Telegram, and MAX;
- participant profiles;
- routes and GPX;
- logistics and load distribution;
- warehouse balances;
- procurement prices and aggregator integration.

Multi-tenant support remains prohibited.
