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
- Administrator SMTP connection checks and fixed test-message outcomes;
- invitation creation, reissue, revocation, acceptance, and automatic delivery results;
- Product creation/update and successful Product/Recipe catalogue import apply;
- PurchaseList and PurchaseChecklist generation, responsible-person updates, and checklist item progress;
- RecipeEquipmentRequirement create/update/delete;
- EquipmentList generation and manual item add/update/delete;
- successful Project and purchase-list document generation.

Product events use entity type `product` and bounded catalogue fields. Successful CSV apply uses `catalog_import` and stores only import kind plus row/create/skip/component/note counts. CSV content, row values, and validation details are excluded.

Purchase generation events snapshot Project/MealPlan IDs, workflow status, and bounded counts. Manual changes record semantic before/after state. Calls made with `commit=False` append events to the Project preparation transaction. Audit failure rolls back pending purchase/checklist/equipment writes, and unchanged values do not create events.

Recipe equipment events use `recipe_equipment_requirement`; project equipment uses `equipment_list` and `equipment_list_item`. Snapshots contain names, quantities, calculated/manual/removed state, and parent IDs only. Recalculation and AuditEvent persistence share the existing write transaction.

Document generation events use `project_document` or `purchase_list_document`. They are committed after successful generation and before response delivery. Payloads contain document kind, format, content type, and size only; generated content and filenames are not persisted.

Invitation lifecycle events use entity type `invitation` and the Invitation ID. Create, reissue, revoke, and accept events share the invitation/user/session transaction. Automatic delivery remains after create/reissue commit; its separate event contains only status, attempt count, recipient domain, operation kind, and role. Delivery or delivery-audit failure does not invalidate the invitation or remove the one-time manual link.

Raw tokens, acceptance URLs, passwords and hashes, sessions and hashes, SMTP secrets, provider messages, protocol transcripts, exception details, full recipient addresses, CSV bodies, generated document bytes/text, filenames, and arbitrary request bodies are excluded.

Automatic ORM-wide auditing remains rejected.

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
- lifecycle and equipment-requirement writes append immutable semantic AuditEvents.

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
- Product creation/update validates name/category;
- Recipe creation/rename and Product component writes validate the same rule;
- Dish creation/update validates its name and every Recipe variant;
- Recipe submit/publish/restore activation paths revalidate content;
- Product and Recipe CSV preview/apply use the same policy wrapper;
- runtime policy violations return HTTP 422;
- active Product lists exclude archived Products;
- fuzzy/external classification, exceptions, and allowlists are not implemented.

Alembic `h10021` archives prohibited Product/Recipe/Dish records in dependency order while preserving historical relationships. Products, Recipes, components, and notes can otherwise be loaded through CSV preview/apply. Invalid input does not create partial catalogue data.

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
- missing preparation prevents a partial complete export;
- successful generation/download requests append safe actor-attributed metadata without persisting files.

MailSettings owns non-secret SMTP metadata. The deployment-managed value remains external. Working delivery supports connection checks, a fixed Russian test message, and best-effort invitation delivery with manual fallback. Queues, scheduled retries, persisted delivery history, templates, attachments, and bounce handling are deferred.

## Future domains

- participant profiles;
- routes and GPX;
- logistics and load distribution;
- warehouse balances;
- procurement prices and aggregator integration.

Multi-tenant support remains prohibited.
