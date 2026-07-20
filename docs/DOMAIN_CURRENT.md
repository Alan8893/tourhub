# TourHub Current Domain Model

Status: Active

Last updated: 2026-07-20

## Purpose

This document describes the implemented domain baseline. `PRODUCT_SPEC.md` describes approved target scope. Deferred capabilities are not current implementation.

## Club, identity, and access

One installation represents one tourist club. Multi-tenant support is prohibited.

Implemented identity model:

- one-time bootstrap creates the first active Administrator;
- later users are created only by accepting Administrator-issued one-time invitations;
- approved roles are `administrator`, `instructor`, and `verified_instructor`;
- one User may own multiple independent server sessions;
- raw session and invitation values are never persisted;
- Backend resolves the current User, role, and active state for every authorized request;
- deactivation revokes every active session for the affected User;
- at least one active Administrator must always remain;
- user updates use optimistic versions and stale writes return HTTP 409.

Active users with any approved role may use preparation workflows. System Settings, invitation management, user administration, SMTP operations, and audit reads are Administrator-only.

Per-project ownership, private projects, user profiles, account recovery, and session administration remain future capabilities.

## AuditEvent

AuditEvent is the append-only history record introduced by TH-0089 / ADR-023.

```text
AuditEvent
  ├─ actor_user_id: int?
  ├─ actor_display_name
  ├─ actor_email
  ├─ actor_role
  ├─ action
  ├─ entity_type
  ├─ entity_id?
  ├─ before_data: JSON?
  ├─ after_data: JSON?
  ├─ context_data: JSON
  └─ created_at
```

Actor identity fields are snapshots. Safe JSON is recursively bounded and removes credential/session/secret keys. AuditEvent is added to the same transaction as its business mutation when the write is database-transactional. Normal update/delete operations are rejected.

Current semantic actions cover:

- user role and active-state administration;
- Recipe submit, publish, and reject transitions;
- Project creation, participant recalculation, generation-mode changes, and full preparation;
- initial/regenerated MealPlan creation and manual MealSlot Dish add/remove/replace;
- Club, Appearance, Document Appearance, Module, Invitation Policy, and Mail Settings changes;
- Administrator SMTP connection checks and fixed test-message outcomes.

Settings events use entity type `system_settings` with the typed section as entity ID. They include only changed normalized fields and versions, and no-op saves create no event. Club image changes contain only configured state, MIME type, and byte size. Mail operation events use entity type `mail` and contain bounded status, attempts, optional recipient, and non-secret operation context. SMTP passwords, environment values, protocol transcripts, exception details, invitation values, session values, tokens, and arbitrary request bodies are excluded.

Later domain writes still require explicit instrumentation. Automatic ORM-wide auditing remains rejected.

## Project and MealPlan

Project is the preparation root for one trip. It stores name, participant count, duration, optional start date, first/last meals, Recipe generation mode, status, and preparation results.

Supported Recipe generation modes:

- `club_only` — eligible published CLUB variants only;
- `club_and_personal` — published CLUB variants followed by current-actor PERSONAL variants;
- `personal_preferred` — current-actor PERSONAL variants followed by CLUB fallback.

MealSlotDish persists the exact selected `recipe_id`. Generation, manual assignments, shopping, equipment, and exports use this snapshot rather than re-reading a mutable Dish default. Archived catalogue records remain available to historical assignments but are excluded from new generation.

## Dish and Recipe

Dish and Recipe are separate entities.

```text
Dish
  ├─ recipe_id: published CLUB default
  ├─ is_archived
  ├─ archived_by_alcohol_policy
  ├─ DishRecipeVariant[] ordered by position
  └─ DishMealRole[]
```

Dish rules:

- the default Recipe is required, active, published, CLUB, policy-allowed, and included in the variant set;
- the complete variant set is replaced atomically and preserves caller order;
- additional variants may be active published CLUB Recipes or active PERSONAL Recipes owned by the current actor;
- unrelated PERSONAL or archived/policy-prohibited Recipes are not accepted;
- active Dish reads and preparation repositories exclude archived Dishes;
- archived Dishes remain available through existing historical foreign-key relationships;
- removing/reordering variants does not change existing assignment Recipe snapshots.

```text
Recipe
  ├─ scope: club | personal
  ├─ owner_user_id: User?
  ├─ lifecycle_status: draft | submitted | rejected | published
  ├─ submission and review metadata
  ├─ is_archived
  ├─ archived_by_alcohol_policy
  ├─ RecipeComponent[]
  ├─ RecipeNote[]
  └─ RecipeEquipmentRequirement[]
```

Recipe rules:

- CLUB has no owner and is `published`;
- PERSONAL has one owner and is `draft`, `submitted`, or `rejected`;
- submitted recipes are locked against ordinary edits;
- publication converts PERSONAL to CLUB while preserving submitter attribution;
- policy validation applies to Recipe names and every Product component;
- submit and publish revalidate current content before state transition;
- restore rejects policy-archived Recipes and revalidates ordinary archived content;
- policy-archived Recipes remain readable historically but cannot return to active selection;
- every submit, publish, and reject transition also appends immutable AuditEvent history.

Preparation technology, dietary/season metadata, richer categories, preference weights, per-meal manual Recipe switching, and moderation notifications remain incomplete.

## Product, import, and alcohol policy

Product is independent of Recipes. Practical calculation modes include per-person, fixed-group, and package-per-people.

```text
Product
  ├─ name
  ├─ category
  ├─ unit
  ├─ package_size
  ├─ is_archived
  └─ archived_by_alcohol_policy
```

The central no-exceptions alcohol policy is implemented through ADR-025:

- Unicode NFKC, case-folding, `ё → е`, punctuation tokenization, and complete-word matching;
- one explicit versioned Russian/English vocabulary;
- Product creation validates name/category;
- Recipe creation/rename and Product component writes validate the same rule;
- Dish creation/update validates its name and every Recipe variant;
- Recipe submit/publish/restore activation paths revalidate content;
- Product and Recipe CSV preview/apply use the same policy wrapper;
- runtime policy violations return HTTP 422;
- active Product lists exclude archived Products;
- fuzzy/external classification, exceptions, and allowlists are not implemented.

Alembic `h10021` handles existing data in order:

1. archive prohibited Products by name/category;
2. archive Recipes by name or prohibited Product component;
3. archive Dishes by name or prohibited default Recipe.

Policy markers distinguish automatic archival. A valid Dish with only an archived non-default variant is not archived as a whole; that variant becomes unavailable for future writes/generation. Historical relationships and exports remain readable.

Products, Recipes, components, and notes can otherwise be loaded through CSV preview/apply. Invalid input does not create partial catalogue data.

## Shopping and equipment

Products aggregate across exact Recipes stored on MealSlotDish and compatibility MealPlanItem assignments. Package count, purchase quantity, purchased quantity, surplus, checklist state, comments, responsible person, equipment quantities, overrides, and removals are persisted.

Participant-count changes, menu edits, assignment changes, and relevant Recipe changes refresh prepared outputs. Changing a Dish default or archiving a catalogue record does not reinterpret historical assignment snapshots.

## Documents and mail

`ConsolidatedProjectDocumentDTO` is a non-persisted immutable export snapshot assembled from one prepared Project, MealPlan, exact MealSlotDish Recipes, PurchaseList, optional PurchaseChecklist, EquipmentList, warnings, comments, and responsible-person text.

Implemented document behavior:

- complete Russian PDF sections for Project parameters, menu, loadout, shopping, equipment, warnings, and comments;
- workbook sheets `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование` in fixed order;
- one immutable club/document appearance snapshot per package request;
- focused purchase/equipment files remain compatible;
- the coordinated ZIP includes complete and compatibility artifacts;
- missing preparation prevents a partial complete export.

MailSettings owns non-secret SMTP metadata. The deployment-managed value remains external. Working delivery supports connection checks, a fixed Russian test message, and best-effort invitation delivery with manual fallback. Settings changes and Administrator connection/test outcomes now append safe actor-attributed AuditEvents. Queues, scheduled retries, delivery history, templates, attachments, and bounce handling are deferred.

## Future domains

- participant profiles;
- routes and GPX;
- logistics and load distribution;
- warehouse balances;
- procurement prices and aggregator integration.

Multi-tenant support remains prohibited.
