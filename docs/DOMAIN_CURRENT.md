# TourHub Current Domain Model

Status: Active

Last updated: 2026-07-18

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

Active users with any approved role may use current preparation workflows. System Settings, invitation management, user administration, SMTP connection checks, and test-message actions are Administrator-only.

Per-project ownership, private projects, user profiles, account recovery, session administration, and actor-aware audit remain future capabilities.

## Project

Project is the preparation root for one trip. It stores name, participant count, duration, optional start date, first meal, last meal, status, and preparation results.

`/projects` lists projects. `/projects/{id}` opens one project workspace.

Project creation validates supported meal types and one-day meal ordering in Backend. Participant-count changes preserve selected dishes and recalculate persisted purchasing and equipment data transactionally where affected.

Current projects are shared inside the one-club preparation space. Project ownership and row-level access are not implemented.

## Meal plan

MealPlan contains MealPlanDay records. MealSlot represents one meal occurrence. MealSlotDish is the persisted membership of one Dish in a MealSlot and has its own identifier and order.

The API exposes MealSlotDish identifiers so add, replace, and remove operations address the persisted membership rather than the Dish catalogue record. Source Dish identity is exposed separately as `dish_id`.

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
- archived-recipe and unclassified dishes are excluded from automatic selection;
- missing or exhausted required pools leave the automatic position empty and return a deterministic warning;
- incompatible dishes are never used as a hidden fallback;
- manually edited MealSlots remain authoritative during regeneration, including intentionally empty manual slots;
- generation warnings are stored as the latest successful snapshot and returned on later reads;
- generated compositions persist through MealSlot/MealSlotDish and compatibility MealPlanItem rows.

Legacy MealPlanItem remains a compatibility path. Larger diversity thresholds and future preference modes require separate approved requirements.

## Dish and recipe

Dish and Recipe are separate entities.

Current persistence stores exactly one selected `recipe_id` on each Dish. Users can create and rename dishes and replace the assigned active recipe. A recipe archived after assignment remains visible historically but cannot be newly assigned to a Dish or MealSlot.

Dish owns normalized meal classification:

```text
Dish
  └─ DishMealRole[]
       ├─ role: main | addition | drink | snack
       ├─ is_repeatable
       └─ allowed MealType[]
```

Compatibility is stored per `(dish_id, role, meal_type)`. A Dish may have multiple roles with independent repeatability and meal-type compatibility. Unclassified dishes remain valid for manual selection but are excluded from automatic generation.

The backend validates:

- `main`, `addition`, and `drink` only for breakfast/lunch/dinner;
- `snack` only for snack;
- at least one compatible meal type for every selected role;
- unique roles and unique meal-type assignments.

Dish recipe replacement recalculates affected persisted purchasing and equipment projections in the same transaction.

The implemented Recipe shape through TH-0087 / ADR-021 is:

```text
Recipe
  ├─ scope: club | personal
  ├─ owner_user_id: User?
  ├─ lifecycle_status: draft | submitted | rejected | published
  ├─ submitted_by_user_id: User?
  ├─ submitted_at
  ├─ reviewed_by_user_id: User?
  ├─ reviewed_at
  ├─ review_comment
  ├─ is_archived
  ├─ RecipeComponent[]
  ├─ RecipeNote[]
  └─ RecipeEquipmentRequirement[]
```

Persistence constraints enforce:

- CLUB has no owner and is `published`;
- PERSONAL has one owner and is `draft`, `submitted`, or `rejected`;
- all pre-existing CLUB recipes migrate to `published`;
- every interactive new Recipe is a PERSONAL `draft` owned by the current actor;
- submitted and rejected recipes retain submitter metadata;
- rejection requires reviewer, review time, and a non-empty comment.

Visibility and lifecycle policy:

- Administrator sees all recipes and may review any submitted recipe;
- Verified Instructor sees CLUB plus owned PERSONAL recipes in the normal library and may edit CLUB plus owned editable PERSONAL recipes;
- Verified Instructor has a separate queue for other users' submitted recipes and cannot self-review;
- Instructor sees CLUB plus owned PERSONAL recipes and may edit owned `draft` or `rejected` recipes;
- unrelated PERSONAL drafts and rejections are returned as not found;
- the owner may submit `draft` or `rejected`; resubmission clears the previous decision;
- `submitted` blocks root, component, note, equipment, and archive changes;
- publication converts PERSONAL to CLUB, clears current owner, and preserves submitter attribution;
- rejection returns the recipe to the owner with the latest required comment;
- permanent deletion remains Administrator-only and recipes already used by a Dish remain non-deletable.

Submit, publish, and reject transitions lock the Recipe row before validating state. Full moderation history, multiple Recipe variants per Dish, generation modes, preparation technology, dietary metadata, season metadata, and richer categories remain incomplete.

## Product and import

Product is independent of recipes. Practical calculation modes include per-person, fixed-group, and package-per-people.

Products, recipes, components, and notes can be loaded through CSV preview and apply operations. Trusted internal import paths continue to create shared published CLUB catalogue records; invalid input does not create partial catalogue data.

Product update and deletion are not implemented. The approved alcohol prohibition rule still requires centralized Backend enforcement for API and import paths.

## Shopping and packaging

Products are aggregated across RecipeComponents and legacy ingredients. Package count is rounded up and persisted with required quantity, purchased quantity, and remainder.

Recalculation triggers include participant-count changes, MealSlot edits, Dish recipe replacement, and relevant recipe changes. Checklist state is preserved for products that remain after refresh. MealSlot mutations and their purchasing refresh share one commit/rollback boundary.

The current workflow persists checklist state, comments, surplus presentation, and optional responsible-person text. Prices, shops, stock balances, and procurement aggregation remain future work.

## Equipment

Equipment requirements are attached to recipes and persisted into project equipment lists.

Implemented behavior:

- identical requirements are aggregated by maximum simultaneously required quantity rather than summed across trip days;
- participant, menu, Dish recipe, and recipe-requirement changes refresh prepared project equipment;
- manual rows, quantity overrides, and removals are persisted;
- user-facing equipment values are included in Russian PDF, Excel, print, and ZIP outputs.

Warehouse balances, issue workflow, and participant/team distribution remain future domains.

## Documents and mail

Current document output includes Russian purchasing and equipment PDF, Excel, print, and coordinated ZIP artifacts using one immutable club/document settings snapshot per generation request.

The complete consolidated PDF and workbook contents described in `PRODUCT_SPEC.md` remain release-blocking future work.

MailSettings owns non-secret SMTP metadata. The deployment-managed value remains external. Working delivery supports connection checks, a fixed Russian test message, and best-effort invitation delivery with a manual-link fallback. Queues, scheduled retries, delivery history, arbitrary templates, attachments, and bounce handling are deferred.

## Future domains

- participant profiles;
- routes and GPX;
- logistics and load distribution;
- warehouse balances;
- procurement prices and aggregator integration.

Multi-tenant support remains prohibited.
