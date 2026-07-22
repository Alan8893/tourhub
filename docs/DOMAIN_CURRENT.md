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

A User owns one editable personal contact profile with FIO, read-only login email, optional phone/Telegram/MAX/VK, role, active state, and version. Contact values are exposed to another user only through shared Project-team access. Only an active Administrator may read or export the club-wide AuditEvent journal.

## AuthSession and own-session projection — TH-0107

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

The personal-account projection exposes only ID, creation, last-seen, expiry, and current marker. A User receives only their own active non-expired sessions; the current login is matched by hashing the HttpOnly cookie in Backend. Another owned session may be revoked, unrelated/revoked/expired/unknown IDs return not found, and current-login termination remains ordinary logout. Revocation and `account_session_revoked` share one transaction. Token, cookie, header, IP/device/user-agent/fingerprint/location data are excluded.

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
```

Every production Project has one owner and any number of additional instructors. Owner and additional membership are mutually exclusive. Administrators may participate as additional instructors without changing global role. `h10023` backfills ownership from trustworthy `project_created` audit history with first-Administrator fallback.

Administrator, owner, and additional-instructor capabilities are Backend-controlled. Outsiders receive no catalogue item and HTTP 404 for direct/nested access. `completed` is terminal read-only history and cannot be reopened. Future `Копировать проект` creates a new identity and is not implemented.

## Product archive lifecycle — TH-0108

`Product` persists the lifecycle fields required for soft archive:

```text
Product
  ├─ id
  ├─ name
  ├─ category?
  ├─ unit
  ├─ package_size?
  ├─ is_archived
  └─ archived_by_alcohol_policy
```

Rules:

- the active Product projection contains only `is_archived = false` rows and remains the source for new Recipe components;
- the explicit archive projection contains archived rows plus policy-lock state;
- archive sets `is_archived = true` and never deletes Product or dependent historical references;
- manually archived Product restore sets `is_archived = false` only after the stored name/category passes the central alcohol policy;
- `archived_by_alcohol_policy = true` is a permanent restore lock for this capability;
- archive and restore lock the Product row and append `product_archived` or `product_restored` in the same transaction;
- repeated archive/restore calls are idempotent and create no duplicate event;
- stable Recipe/Product response contracts remain separate from archive-management DTOs.

## Dish archive lifecycle — TH-0109

`Dish` already persists the lifecycle fields required for soft archive:

```text
Dish
  ├─ id
  ├─ name
  ├─ recipe_id → Recipe
  ├─ RecipeVariant[]
  ├─ MealRole[]
  ├─ is_archived
  └─ archived_by_alcohol_policy
```

Rules:

- the active Dish projection contains only `is_archived = false` rows and remains the source for catalogue readiness, manual selection, and generation;
- the explicit archive projection contains archived rows, primary Recipe display data, and policy-lock state;
- archive sets `is_archived = true` and never deletes Dish, variants, roles, or historical MealSlot/project references;
- manually archived Dish restore sets `is_archived = false` only after the stored name passes the central alcohol policy;
- `archived_by_alcohol_policy = true` is a permanent restore lock for this capability;
- archive and restore lock the Dish row and append `dish_archived` or `dish_restored` in the same transaction;
- repeated archive/restore calls are idempotent and create no duplicate event;
- stable Dish/Recipe response contracts remain separate from archive-management DTOs.

## Project team contacts

Project team projection contains owner first and additional instructors in deterministic order, with global role, Project role, active state, and contact fields. Active authorized viewers receive approved mail/phone/social/vCard actions; inactive historical members remain identifiable but expose no actions. The former club-wide contact directory is removed.

## AuditEvent

AuditEvent is append-only and stores actor snapshots, semantic action, entity identity, safe before/after/context JSON, and timestamp.

Current relevant actions include:

- `account_profile_updated`;
- `account_password_changed`;
- `account_session_revoked`;
- `product_created`;
- `product_updated`;
- `product_archived`;
- `product_restored`;
- `dish_archived`;
- `dish_restored`.

For Product and Dish archive actions, entity type and ID identify the lifecycle row, before/after use bounded snapshots, and context contains only `policy_locked`. State and AuditEvent share one transaction; audit failure rolls back state. No-op writes create no event. Credentials, tokens, cookies, headers, raw request bodies, unrelated catalogue rows, source CSV bodies, and document contents are excluded. Automatic ORM-wide auditing remains rejected.

### Audit CSV projection — TH-0106

CSV export is a read projection over existing AuditEvent rows. It is Administrator-only, shares list filters, serializes sanitized mappings deterministically, neutralizes spreadsheet formula prefixes, and rejects exports above 10,000 rows. It creates no AuditEvent and mutates no domain state.

## Menu, catalogue, documents, and mail

MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only. MealSlotDish persists the exact selected Recipe. Project Recipe generation modes remain `club_only`, `club_and_personal`, and `personal_preferred`.

Product, Recipe ownership/lifecycle, Dish Recipe variants, exact assignment snapshots, archive state, and the central no-exceptions alcohol policy remain Backend-owned. Archived Product and Dish rows remain readable through existing historical relationships while being excluded from new active selection.

Consolidated Project documents remain non-persisted immutable snapshots. Authorized members may generate/download approved documents; completed Projects retain read-only document access. MailSettings and invitation delivery retain existing boundaries. Project-team notifications remain a no-op boundary.

## Current migrations

- released `v0.1.0`: `h10021`;
- optional User contact profile: `h10022`;
- Project owner/team membership: `h10023` current single head;
- TH-0106 Audit CSV Export: no migration;
- TH-0107 Session Administration: no migration;
- TH-0108 Product Archive Management: no migration because Product archive columns already existed;
- TH-0109 Dish Archive Management: no migration because Dish archive columns already existed.

## Future domains and tasks

- copy a completed Project into a new Project template instance;
- audit retention policy/UI after required Product Owner decisions;
- global sign-out, Administrator session administration, and session cleanup;
- ownership-aware CSV import UX;
- Project-team notifications through email, Telegram, and MAX;
- participant profiles, routes/GPX, logistics, warehouse, and procurement integrations.

No post-release product task is active after TH-0109. Multi-tenant support and microservices remain prohibited.
