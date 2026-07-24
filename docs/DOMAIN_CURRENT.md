# TourHub Current Domain Model

Status: Active

Last updated: 2026-07-24

## Purpose

This document describes the implemented domain baseline. `PRODUCT_SPEC.md` describes approved target scope. Deferred capabilities are not current implementation.

## Club, identity, and access

One installation represents one tourist club. Multi-tenant support is prohibited.

- one-time bootstrap creates the first active Administrator;
- later users are created only through Administrator-issued invitations;
- one User has one global role: `administrator`, `instructor`, or `verified_instructor`;
- one User may own multiple independent server sessions;
- active state is checked on every authorized request;
- deactivation revokes sessions and removes runtime Project access;
- at least one active Administrator must remain;
- personal contact values are exposed to another user only through shared Project-team access.

## Recipe ownership and lifecycle

```text
Recipe
  ├─ id
  ├─ name (club-wide unique)
  ├─ scope: club | personal
  ├─ owner_user_id? → User
  ├─ lifecycle_status: draft | submitted | published | rejected
  ├─ RecipeComponent[]
  ├─ RecipeNote[]
  └─ is_archived
```

- CLUB Recipes have no owner and are published;
- PERSONAL Recipes have one owner and use draft/submitted/rejected lifecycle until moderation;
- visible projection contains CLUB Recipes and personal Recipes owned by the current user, while Administrators retain site-wide visibility;
- MealSlotDish persists the exact selected Recipe identity used by the menu.

## Ownership-aware Recipe CSV import — TH-0110

Recipe CSV rows do not contain ownership columns. Ownership is one operation-level target.

- `club` creates published ownerless Recipes and `personal` creates current-user-owned drafts;
- every component row references an existing Product and repeated note tuples are deduplicated;
- existing names, missing Products, malformed values, duplicate constraints, and alcohol policy remain validation errors;
- preview creates no state and returns a token bound to actor, exact content, and scope;
- explicit apply requires the matching token and re-runs validation;
- mismatch returns HTTP 409 with no Recipe/component/note/AuditEvent write;
- successful state and bounded `catalog_import_applied` audit commit together;
- Product import and legacy validated Recipe CLUB apply remain compatible.

## Project ownership, team, and copy

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

Every production Project has one owner and any number of additional instructors. Owner and additional membership are mutually exclusive. Administrators may participate without changing global role. `completed` is terminal read-only history and cannot be reopened.

### Copy Project — TH-0111

Copy is a command over completed Project history, not a lifecycle transition on the source.

```text
completed source Project
  + destination creation parameters
  + owner/Administrator actor
  → new draft Project identity owned by actor
  → new MealPlan/Day/MealSlot identities
  → matching usable MealSlotDish assignments
  → bounded project_copied AuditEvent
```

Rules:

- source must be completed, visible, and owned by the actor unless the actor is an Administrator;
- destination fields use the ordinary Project creation contract;
- destination schedule is generated from destination `days`, `first_meal`, and `last_meal`;
- source assignments match by `(day_number, meal_type)`;
- archived Dish or Recipe identity not eligible under current actor/generation mode is skipped with a warning;
- source owner/team, completion, timestamps, purchase/checklist/equipment/readiness/document state, delivery history, and AuditEvents are not copied;
- copied assignments receive new association IDs while retaining selected Dish/Recipe identities;
- repeating the command creates another independent Project;
- destination state and audit roll back together on any failure.

## Product archive lifecycle — TH-0108

Active projection is used for new Recipe components. Explicit archive projection exposes policy-lock state. Archive is soft, restore re-runs central alcohol policy, policy-locked rows remain non-restorable, and state plus `product_archived` / `product_restored` share one transaction.

## Dish archive lifecycle — TH-0109

Active projection remains the source for catalogue readiness, manual selection, generation, and Project-copy dependency checks. Archive preserves variants, roles, and historical MealSlot/project references. Restore re-runs central policy and state plus `dish_archived` / `dish_restored` share one transaction.

## AuthSession and own-session projection

A User receives only their own active non-expired sessions; the current login is matched by hashing the HttpOnly cookie in Backend. Another owned session may be revoked, unrelated/revoked/expired/unknown IDs return not found, and current-login termination remains ordinary logout. Token, cookie, header, IP/device/user-agent/fingerprint/location data are excluded.

## AuditEvent

AuditEvent is append-only and stores actor snapshots, semantic action, entity identity, safe before/after/context JSON, and timestamp.

Relevant actions include account/profile/session, Product/Dish lifecycle, Project/team/preparation/copy, shopping/checklist/equipment/documents, and `catalog_import_applied`.

State and AuditEvent share the owning transaction; audit failure rolls back state. `project_copied` contains bounded source/destination and copied/skipped counts rather than full menu snapshots. Credentials, tokens, cookies, headers, raw request bodies, unrelated catalogue rows, source CSV bodies, preview tokens, and document contents are excluded. Automatic ORM-wide auditing remains rejected.

### Audit CSV projection — TH-0106

CSV export is an Administrator-only read projection over existing AuditEvent rows. It shares list filters, serializes sanitized mappings deterministically, neutralizes spreadsheet formula prefixes, rejects exports above 10,000 rows, creates no AuditEvent, and mutates no domain state.

## Menu, catalogue, documents, and mail

MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only. Project Recipe generation modes remain `club_only`, `club_and_personal`, and `personal_preferred`.

Product, Recipe ownership/lifecycle, Dish Recipe variants, exact assignment identities, archive state, import ownership, Project-copy dependency eligibility, and central no-exceptions alcohol policy remain Backend-owned. Archived rows remain readable through historical relationships while being excluded from new active selection and copy projection.

Consolidated Project documents remain non-persisted immutable snapshots. MailSettings and invitation delivery retain existing boundaries. Project-team notifications remain a no-op boundary.

## Current migrations

- released `v0.1.0`: `h10021`;
- optional User contact profile: `h10022`;
- Project owner/team membership: `h10023` current single head;
- TH-0106 Audit CSV Export: no migration;
- TH-0107 Session Administration: no migration;
- TH-0108 Product Archive Management: no migration;
- TH-0109 Dish Archive Management: no migration;
- TH-0110 Ownership-Aware CSV Import: no migration;
- TH-0111 Copy Project: no migration because existing Project/MealPlan/MealSlot/Audit persistence is reused.

## Future domains and tasks

- audit retention policy/UI after required Product Owner decisions;
- global sign-out, Administrator session administration, and session cleanup;
- Project-team notifications and reusable team templates;
- richer Recipe metadata, participant profiles, routes/GPX, logistics, warehouse, and procurement integrations.

No post-release product task is active after TH-0111. Multi-tenant support and microservices remain prohibited.
