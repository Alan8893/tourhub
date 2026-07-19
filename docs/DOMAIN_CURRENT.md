# TourHub Current Domain Model

Status: Active

Last updated: 2026-07-19

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

Rules:

- actor display name, email, and role are snapshots at action time;
- actor identity is not joined through a live User foreign key, so history survives later account changes;
- safe JSON is recursively bounded and removes password, hash, credential, cookie, session, token, authorization, and secret keys;
- AuditEvent is added to the same transaction as its business mutation;
- normal ORM update and delete operations are rejected;
- the application exposes Administrator-only filtered reads and no AuditEvent mutation API;
- current semantic actions cover user role/activation changes and Recipe submit/publish/reject transitions;
- later domain write paths require explicit semantic instrumentation.

Existing `SystemSettingsHistory` remains a separate bounded compatibility history for focused settings screens.

## Project

Project is the preparation root for one trip. It stores name, participant count, duration, optional start date, first meal, last meal, Recipe generation mode, status, and preparation results.

Supported Recipe generation modes:

- `club_only` — use eligible published CLUB variants only;
- `club_and_personal` — use published CLUB variants first, then PERSONAL variants owned by the current actor;
- `personal_preferred` — use current-actor PERSONAL variants first, then published CLUB fallback.

Project creation validates meal boundaries and generation mode in Backend. Changing the mode affects later generation and manual Dish assignment; it does not rewrite existing assignment Recipe snapshots.

Current projects remain shared inside the one-club preparation space. Project ownership and row-level access are not implemented.

## Meal plan

MealPlan contains MealPlanDay records. MealSlot represents one meal occurrence. MealSlotDish is the persisted membership of one Dish in a MealSlot and has its own identifier, order, and selected `recipe_id`.

The API and complete exports expose MealSlotDish identity, source `dish_id`, exact selected `recipe_id`, Dish name, and Recipe name. Compatibility MealPlanItem also stores the selected Recipe.

Implemented generation behavior:

- first/last meal boundaries and one-day trip ranges;
- domain order `breakfast`, `snack`, `lunch`, `dinner`;
- breakfast, lunch, and dinner require a compatible `main` role;
- snack requires a compatible `snack` role;
- compatible `addition` and `drink` roles are optional;
- stable composition order `main → addition → drink`;
- same-day uniqueness for non-repeatable assignments;
- non-repeatable main-dish diversity uses trip calendar days and permits reuse on day four;
- repeatability is evaluated per `(dish, role)` assignment;
- Dishes without an eligible Recipe under the current Project mode are excluded;
- missing required pools leave the automatic position empty and return a deterministic warning;
- repeated occurrences rotate deterministically through eligible ordered Recipe variants;
- manually edited MealSlots remain authoritative during regeneration, including intentionally empty slots and selected Recipes;
- generation warnings are persisted as the latest successful snapshot;
- generated compositions persist through MealSlot/MealSlotDish and compatibility MealPlanItem rows.

Legacy MealPlanItem remains a compatibility path.

## Dish and Recipe

Dish and Recipe are separate entities.

```text
Dish
  ├─ recipe_id: published CLUB default
  ├─ DishRecipeVariant[] ordered by position
  │    └─ recipe_id
  └─ DishMealRole[]
       ├─ role: main | addition | drink | snack
       ├─ is_repeatable
       └─ allowed MealType[]
```

Dish rules:

- the default Recipe is required, active, published, CLUB, and included in the variant set;
- the complete variant set is replaced atomically and preserves caller order;
- additional variants may be active published CLUB Recipes or active PERSONAL Recipes owned by the current actor;
- unrelated PERSONAL Recipes are not accepted or projected;
- removing or reordering a variant does not change existing assignment Recipe snapshots;
- archiving a Recipe keeps historical assignments readable but makes it ineligible for new assignment;
- permanent Recipe deletion remains blocked when a Dish or persisted assignment uses it.

Dish role compatibility is stored per `(dish_id, role, meal_type)`. Unclassified dishes remain valid for manual selection but are excluded from role-aware automatic generation.

```text
Recipe
  ├─ scope: club | personal
  ├─ owner_user_id: User?
  ├─ lifecycle_status: draft | submitted | rejected | published
  ├─ submission and review metadata
  ├─ is_archived
  ├─ RecipeComponent[]
  ├─ RecipeNote[]
  └─ RecipeEquipmentRequirement[]
```

Persistence and lifecycle constraints enforce:

- CLUB has no owner and is `published`;
- PERSONAL has one owner and is `draft`, `submitted`, or `rejected`;
- interactive creation produces an owned PERSONAL `draft`;
- submitted/rejected recipes retain submitter metadata;
- rejection requires reviewer, review time, and non-empty feedback;
- submitted recipes are locked against ordinary root/component/note/equipment/archive changes;
- publication converts PERSONAL to CLUB and preserves submitter attribution;
- resubmission clears the previous decision;
- Administrator may review any submission;
- Verified Instructor may review another user's submission but cannot self-review;
- Instructor edits owned `draft` or `rejected` recipes;
- unrelated PERSONAL drafts/rejections are returned as not found;
- every submit, publish, and reject transition also appends immutable actor-aware AuditEvent history.

Preparation technology, dietary metadata, season metadata, richer categories, preference weights, per-meal manual Recipe switching, and moderation notifications remain incomplete.

## Product and import

Product is independent of Recipes. Practical calculation modes include per-person, fixed-group, and package-per-people.

Products, Recipes, components, and notes can be loaded through CSV preview/apply. Trusted internal import paths create shared published CLUB catalogue records. Invalid input does not create partial catalogue data.

Product update/deletion and the approved centralized alcohol prohibition remain incomplete.

## Shopping and packaging

Products aggregate across the exact Recipes stored on MealSlotDish and compatibility MealPlanItem assignments. Package count is rounded up and persisted with required quantity, purchased quantity, and remainder.

Participant-count changes, menu edits, manual assignment changes, and relevant Recipe component changes refresh persisted purchasing where affected. Changing the mutable Dish default alone does not reinterpret historical assignments. Checklist state is preserved for products that remain after refresh.

Prices, shops, stock balances, and procurement aggregation remain future work.

## Equipment

Equipment requirements are attached to Recipes and projected from the exact Recipe selected on each meal assignment.

Identical requirements aggregate by maximum simultaneously required quantity. Manual rows, quantity overrides, and removals are persisted. Warehouse balances, issue workflow, and participant/team distribution remain future domains.

## Documents and mail

`ConsolidatedProjectDocumentDTO` is a non-persisted immutable export snapshot assembled from one prepared Project, its MealPlan, exact MealSlotDish Recipes, PurchaseList, optional PurchaseChecklist, EquipmentList, warnings, comments, and responsible-person text.

Implemented document behavior:

- complete Russian PDF sections: Project parameters, menu by day, food loadout, shopping, equipment, warnings, and comments;
- complete Russian workbook sheets in fixed order: `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование`;
- menu rows use the persisted assignment Recipe rather than the current Dish default;
- shopping rows include requirements, package size/count, purchase quantity, surplus, checklist progress, and comments;
- equipment rows use persisted final quantities and source labels;
- one immutable club/document appearance snapshot is reused for all artifacts generated by one package request;
- focused purchase/equipment PDF, XLSX, and print outputs remain compatible;
- the coordinated ZIP includes complete PDF/XLSX plus compatibility artifacts;
- missing menu, purchasing, or equipment preparation prevents a partial complete export.

MailSettings owns non-secret SMTP metadata. The deployment-managed value remains external. Working delivery supports connection checks, a fixed Russian test message, and best-effort invitation delivery with a manual-link fallback. Queues, scheduled retries, delivery history, templates, attachments, and bounce handling are deferred.

## Future domains

- participant profiles;
- routes and GPX;
- logistics and load distribution;
- warehouse balances;
- procurement prices and aggregator integration.

Multi-tenant support remains prohibited.
