# TourHub Current Architecture

Status: Active

Last updated: 2026-07-20

TourHub is a single-club modular monolith with PostgreSQL in production.

## Current decisions

- System Settings use independent typed owners under one responsive surface: ADR-014.
- Accounts, roles, invitations, and user administration follow ADR-015 through ADR-017.
- Preparation access follows ADR-018.
- Working mail delivery follows ADR-019.
- Recipe ownership follows ADR-020.
- Recipe publication and moderation follow ADR-021.
- Dish Recipe variants and project generation modes follow ADR-022.
- Actor-aware audit foundation follows ADR-023.
- Consolidated Project exports follow ADR-024.
- Central alcohol prohibition follows ADR-025.
- Active Administrator, Instructor, and Verified Instructor users may use preparation workflows.
- Settings, invitation management, user management, mail operations, and audit reads remain Administrator-only.
- Module visibility is presentation only and never grants access.
- Frontend route guidance and capability projection never replace Backend permission or policy checks.

## Access runtime

- one User may own multiple independent server sessions;
- PostgreSQL stores only session-token hashes and session metadata;
- Backend resolves the current persisted User on every authorized request;
- deactivation revokes every active session for the affected User in the same transaction;
- protected HTTP 401 responses clear stale frontend identity centrally;
- route guards preserve exact path, query, and hash through sign-in and logout;
- the application header exposes current display name and role;
- session administration, account recovery, project ownership, and row-level ACLs remain separate future capabilities.

## Recipe ownership and lifecycle boundary

- Recipe owns scope, nullable current owner, lifecycle state, submission/decision metadata, archive state, components, notes, and equipment requirements;
- the database permits CLUB only as ownerless `published`, or PERSONAL with an owner as `draft`, `submitted`, or `rejected`;
- interactive creation produces owned PERSONAL drafts;
- unrelated personal recipes are filtered before API projection;
- one centralized Recipe access policy protects root, component, note, equipment, archive, submission, and moderation operations;
- submitted recipes are immutable through ordinary edit paths;
- submit, publish, and reject lock the Recipe row and commit one state transition;
- publication converts PERSONAL to CLUB while preserving submitter attribution;
- rejection requires a comment and resubmission clears the previous decision;
- alcohol content is revalidated before submit, publish, and restore;
- API capabilities guide Frontend controls while Backend services remain authoritative.

## Dish variant and generation boundary

- Dish retains one required `recipe_id` as the published CLUB default and compatibility fallback;
- `DishRecipeVariant` stores the ordered complete variant set by `(dish_id, recipe_id, position)`;
- a write replaces the complete ordered set atomically and the default must be included;
- additional variants may be active published CLUB recipes or active PERSONAL recipes visible to the current actor;
- another user's PERSONAL recipe is neither accepted by writes nor projected in Dish responses;
- Project owns `recipe_generation_mode`: `club_only`, `club_and_personal`, or `personal_preferred`;
- generation rotates deterministically through eligible Recipe variants;
- MealSlotDish and compatibility MealPlanItem persist the exact selected `recipe_id`;
- manually edited slots retain stored Recipes through regeneration;
- shopping, equipment, and consolidated exports read assignment Recipes;
- archived Products, Recipes, and Dishes remain readable through historical relationships but are excluded from new attachment/generation.

## Actor-aware audit boundary

- `AuditEvent` is a separate append-only persistence boundary;
- each event snapshots actor User ID, display name, email, and role at action time without a live User foreign-key dependency;
- events store semantic action, entity type/ID, timestamp, and bounded safe before/after/context JSON;
- recursive normalization removes password, hash, credential, cookie, session, token, authorization, and secret fields;
- business mutation and AuditEvent commit or roll back together when the business write is transactional;
- ORM update/delete attempts fail and the application exposes no mutation endpoint;
- Administrator may query bounded filtered history through `/api/v1/audit/events`;
- explicit coverage includes user access, Recipe moderation, Project preparation, Menu/MealSlot changes, all typed System Settings owners, Administrator mail checks/tests, invitation lifecycle/delivery results, Product writes, successful catalogue imports, shopping/checklist writes, Recipe/project equipment writes, and successful document generation;
- Product, purchase, checklist, Recipe-equipment, and EquipmentList events are staged before the owning commit; audit failure rolls back the pending mutation;
- preparation services invoked with `commit=False` append their events to the caller-owned Project preparation transaction;
- no-op Product, responsible-person, checklist, Recipe-equipment, and equipment-quantity edits create no event;
- catalogue import events contain aggregate kind/row/create/skip/component/note counts only and never CSV content or row details;
- document generation remains a non-persisted byte/string boundary, while its audit event commits before the response and contains only document kind, format, content type, and size metadata;
- invitation delivery-result persistence remains isolated from the already committed invitation so logging failure cannot invalidate it or hide the manual link;
- generated document content, filenames, raw CSV, arbitrary request bodies, raw invitation/session values, passwords/hashes, SMTP secrets, provider messages, transcripts, and exception details are not audit payloads;
- automatic ORM-wide auditing remains rejected.

## Consolidated export boundary

- `ConsolidatedProjectDocumentDTO` is the immutable Backend contract for one prepared export request;
- the mapper combines Project parameters, MealPlan warnings, exact MealSlotDish Dish/Recipe snapshots, purchasing/checklist state, EquipmentList rows, and responsible-person text;
- one club/document appearance snapshot is reused across all files in one package request;
- the complete PDF contains Project parameters, menu, loadout, shopping, equipment, warnings, and comments;
- the complete workbook contains `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование` in order;
- focused purchase/equipment endpoints remain compatible;
- incomplete preparation returns HTTP 409 rather than a partial complete export;
- successful focused, consolidated, package, and legacy purchase-list generation now append bounded actor-attributed audit metadata without persisting generated files.

## Central alcohol policy boundary

- `AlcoholPolicy` is the single Backend classifier for Product, Recipe, Dish, lifecycle activation, and CSV import paths;
- Unicode NFKC, case-folding, `ё → е`, punctuation tokenization, and complete-word matching are deterministic;
- the vocabulary is explicit and versioned; fuzzy/external classification and user exceptions are prohibited for the current release;
- `AlcoholPolicyViolation` is centrally projected as HTTP 422 with one safe Russian message;
- Product and Dish active queries filter `is_archived`;
- Recipe/Dish writes reject archived or policy-prohibited Product/Recipe dependencies;
- `h10021` adds Product/Dish archive state and policy markers on Product, Recipe, and Dish;
- policy-archived records are retained for historical foreign keys, calculations, and exports.

## Mail boundary

- `MailSettings` owns only non-secret SMTP metadata and optimistic version;
- the deployment-managed SMTP value remains in `TOURHUB_SMTP_SECRET` and is never accepted or returned by APIs;
- `MailDeliveryService` owns plain, STARTTLS, implicit TLS, optional authentication, bounded retries, and safe results;
- invitation persistence commits before automatic delivery;
- delivery failure never invalidates the invitation or removes its manual link;
- TH-0101 audits MailSettings changes and Administrator connection/test operations;
- TH-0102 audits safe create/reissue delivery outcomes without changing invitation ownership, delivery behavior, or the manual fallback.

The current Alembic head is `h10021`.

MealSlot and MealSlotDish remain primary. MealPlanItem remains compatibility-only.

Multi-tenancy and microservices remain prohibited.

See `PRODUCT_SPEC.md` and ADR-012 through ADR-025.
