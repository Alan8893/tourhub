# TourHub Current Architecture

Status: Active

Last updated: 2026-07-19

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
- Active Administrator, Instructor, and Verified Instructor users may use preparation workflows.
- Settings, invitation management, user management, connection checks, test-message actions, and audit reads remain Administrator-only.
- Module visibility is presentation only and never grants access.
- Frontend route guidance and capability projection never replace Backend permission checks.

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
- the normal library and moderation queue are separate query views;
- one centralized Recipe access policy protects root, component, note, equipment, archive, submission, and moderation operations;
- submitted recipes are immutable through ordinary edit paths;
- submit, publish, and reject lock the Recipe row and commit one state transition;
- publication converts PERSONAL to CLUB while preserving submitter attribution;
- rejection requires a comment and resubmission clears the previous decision;
- API capabilities guide Frontend controls while Backend services remain authoritative.

## Dish variant and generation boundary

- Dish retains one required `recipe_id` as the published CLUB default and compatibility fallback;
- `DishRecipeVariant` stores the ordered complete variant set by `(dish_id, recipe_id, position)`;
- a write replaces the complete ordered set atomically and the default must be included;
- additional variants may be active published CLUB recipes or active PERSONAL recipes visible to the current actor;
- another user's PERSONAL recipe is neither accepted by writes nor projected in Dish responses;
- Project owns `recipe_generation_mode`: `club_only`, `club_and_personal`, or `personal_preferred`;
- generation groups eligible variants according to the Project mode and rotates deterministically through repeated Dish occurrences;
- MealSlotDish and compatibility MealPlanItem persist the exact selected `recipe_id`;
- manually edited slots retain the stored Recipe through regeneration;
- manual add/replace uses the same Project mode selector;
- shopping, equipment, and consolidated exports read assignment Recipes, so later Dish default or variant edits do not rewrite historical project results;
- Frontend exposes variant scope, owner, default status, Project mode, and stored Recipe without owning selection rules.

## Actor-aware audit boundary

- `AuditEvent` is a separate append-only persistence boundary, not an extension of trimmed focused System Settings history;
- each event snapshots actor User ID, display name, email, and role at action time without a live User foreign-key dependency;
- events store semantic action, entity type/ID, timestamp, and bounded safe before/after/context JSON;
- recursive normalization removes password, hash, credential, cookie, session, token, authorization, and secret fields at every nesting level;
- a service adds its AuditEvent to the same SQLAlchemy Session before committing the business mutation;
- business mutation and audit event therefore commit or roll back together;
- ORM update/delete attempts on AuditEvent fail and the application exposes no mutation endpoint;
- Administrator may query bounded filtered history through `/api/v1/audit/events`;
- TH-0089 instruments user access administration and Recipe submit/publish/reject transitions;
- later domains still require explicit semantic instrumentation.

## Consolidated export boundary

- `ConsolidatedProjectDocumentDTO` is the immutable Backend contract for one prepared export request;
- the mapper combines Project parameters, MealPlan warnings, MealSlotDish Dish/Recipe snapshots, PurchaseList packaging, optional PurchaseChecklist progress/comments, EquipmentList rows, and responsible-person text;
- the menu uses the exact Recipe persisted on MealSlotDish rather than the current Dish default;
- `ProjectDocumentService` resolves one club/document appearance snapshot lazily and reuses it across all files generated by one package service instance;
- the complete PDF contains Project parameters, menu by day, food loadout, shopping, equipment, warnings, and comments;
- the complete workbook contains exactly `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование` in that order;
- existing focused purchase/equipment PDF/XLSX/print endpoints remain compatible;
- the coordinated ZIP contains complete PDF/XLSX plus compatibility artifacts;
- incomplete menu, purchasing, or equipment preparation returns HTTP 409 rather than a partial complete export;
- scheduled generation, email delivery, document persistence, and document-download audit events remain separate capabilities.

## Mail boundary

- `MailSettings` owns only non-secret SMTP metadata and optimistic version;
- the deployment-managed SMTP value remains in `TOURHUB_SMTP_SECRET` and is never accepted or returned by application APIs;
- `MailDeliveryService` owns plain, STARTTLS, implicit-TLS, optional authentication, bounded retries, and safe results;
- invitation persistence commits before automatic delivery;
- delivery failure never invalidates the invitation or removes its manual link;
- queues, background workers, provider APIs, templates, attachments, bounce processing, and delivery history remain future capabilities.

The current Alembic head is `h10020`.

MealSlot and MealSlotDish remain primary. MealPlanItem remains compatibility-only.

Multi-tenancy and microservices remain prohibited.

See `PRODUCT_SPEC.md` and ADR-012 through ADR-024.
