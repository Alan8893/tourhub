# TourHub Technical Debt

Status date: 2026-07-20

## Released through TH-0093 / v0.1.0

- guided preparation, persisted shopping/equipment, recalculation, readiness, and complete Russian document package;
- production-like runtime, backup/restore, health checks, same-origin API proxy, LAN access, and restart persistence;
- typed System Settings through `h10013`;
- invitation-only Access, roles, users, and multi-session readiness through `h10016`;
- working SMTP invitation delivery with manual fallback;
- Recipe CLUB/PERSONAL ownership and nested authorization through `h10017`;
- Recipe lifecycle/moderation through `h10018`;
- Dish Recipe variants, three Project generation modes, and persisted assignment Recipe snapshots through `h10019`;
- append-only actor-aware AuditEvent persistence through `h10020`;
- complete consolidated Russian PDF/XLSX exports and compatibility ZIP package;
- centralized complete-word alcohol policy, archive markers, historical preservation, and `h10021`;
- machine-readable Product Acceptance and Release Readiness contracts;
- PostgreSQL 18 migration-cycle evidence, deployment checklist, exact-head gates, and immutable `v0.1.0` tag;
- backup-based production rollback boundary.

## Release-blocking debt

None. The approved first-release capability scope is feature frozen and release-ready. Any new blocking classification requires reproducible regression, security, migration, or operator evidence.

## Resolved post-release UX debt — TH-0095

- the Project page no longer renders every preparation area as one long landing page;
- compact Overview and stable section URLs replace extensive vertical scrolling;
- Shopping calculation and checklist no longer compete in a narrow two-column layout;
- the sidebar becomes a drawer below desktop width;
- responsive browser acceptance covers 360 px, 831 px, and 1280 px.

## Resolved Product catalogue editing debt — TH-0097

- active shared Products can be edited without recreation;
- Product identifiers and every Recipe relationship remain intact;
- duplicate names and prohibited content preserve established API boundaries;
- changing the catalogue unit does not convert RecipeComponent amount/unit values;
- the Recipe component workflow exposes a responsive edit action and shared-impact warning;
- no migration was required and Alembic remains `h10021`.

## Resolved published Recipe Dish synchronization debt — TH-0098

- every newly published CLUB Recipe is synchronized into Dishes in the publication transaction;
- synchronization and the publication AuditEvent share the same rollback boundary;
- Recipes already attached as a default or variant are not duplicated;
- active exact-name Dishes receive the Recipe as the next variant without changing default Recipe or roles;
- otherwise one active role-less Dish is created with the Recipe as default and only variant;
- role-less Dishes show `Не настроено для генератора` and remain available for manual choice;
- `Настроить генератор` opens the existing explicit role editor;
- after role assignment the Dish shows `Готово для генератора` and updates readiness coverage;
- no role, meal type, or repeatability value is inferred;
- strict Ruff/mypy, transaction rollback tests, full Backend regression, and focused real-Chrome acceptance cover the workflow;
- no migration was required and Alembic remains `h10021`.

## Resolved Project audit debt — TH-0099

- Project creation records `project_created` with the authenticated actor in the creation commit;
- participant changes record `project_participants_updated` in the same transaction as derived purchasing, checklist, and equipment recalculation;
- generation-mode changes record `project_generation_mode_updated` in the Project update commit;
- full preparation records `project_prepared` in one transaction with purchase list, checklist, and equipment writes;
- no-op participant and generation-mode updates create no event;
- failed creation, recalculation, audit recording, or preparation rolls back both domain changes and pending events;
- existing standalone preparation services retain commit-by-default behavior while supporting caller-owned transactions;
- the Administrator Audit UI/API exposes Russian Project labels and filters;
- strict Ruff/mypy, all Backend tests, Product Acceptance, and real-Chrome Audit coverage verify the behavior;
- no migration was required and Alembic remains `h10021`.

## Resolved Menu and MealSlot audit debt — TH-0100

- initial generation and regeneration record `meal_plan_generated` in the MealPlan/Equipment transaction;
- manual add/remove/replace record semantic MealSlot events in the existing derived-refresh transaction;
- bounded snapshots include plan counts, warnings, generation mode, and preserved manual-slot context;
- failures roll back domain changes and pending AuditEvents together;
- the Administrator Audit UI/API exposes Russian Menu and MealSlot labels and filters;
- no migration was required and Alembic remains `h10021`.

## Resolved System Settings and mail audit debt — TH-0101

- Club, Appearance, Document Appearance, Module, Invitation Policy, and Mail Settings changes record real Administrator attribution;
- normalized before/after snapshots contain only changed fields and versions, and no-op saves create no event;
- each settings event shares the existing settings/history commit and rollback transaction;
- Club image changes record only configured state, MIME type, and byte size;
- SMTP connection-check and fixed test-message operations record safe success/failure/unavailable outcomes at the existing result boundary;
- SMTP passwords, environment values, protocol transcripts, exception details, invitation/session values, tokens, and arbitrary request bodies are excluded;
- the Administrator Audit UI/API exposes Russian System Settings and Mail labels and filters;
- strict Ruff/mypy, full Backend regression, real-Chrome acceptance, and release gates verify the behavior;
- no migration was required and Alembic remains `h10021`.

## Remaining audit debt

1. Invitation creation, revocation, acceptance, and delivery-result actions.
2. Catalogue/import, shopping, equipment, and document-generation actions.
3. Audit export, retention UI, external SIEM integration, and operational diagnostics.
4. Undo and event replay remain outside v0.1.0.

Automatic ORM-wide auditing remains rejected; later coverage must use semantic actions and the owning business transaction.

## Remaining Recipe, menu, and catalogue debt

- optional moderation notifications;
- ownership-aware CSV import UX beyond trusted shared-catalogue import;
- preparation technology, dietary metadata, season metadata, and richer categories;
- Recipe-level optimistic-version decision beyond serialized lifecycle transitions;
- per-meal manual Recipe switching without replacing the Dish;
- preference weights beyond the approved generation modes;
- Product/Dish archive-management UI;
- optional role suggestions only after a separately approved deterministic policy; automatic inference remains rejected;
- reviewed policy-vocabulary updates when real catalogue evidence requires them;
- fuzzy/external alcohol classification and user exceptions remain explicitly out of scope.

## Remaining document debt

- scheduled or asynchronous generation;
- email delivery of generated packages;
- persisted document versions or signatures;
- document-download audit events;
- optional formats beyond approved PDF/XLSX/print/ZIP.

## Remaining Access and mail debt

- account recovery and verified email change;
- session administration, individual revocation, cleanup, and global sign-out;
- user profile editing and account-retention policy;
- invitation retention and cleanup;
- asynchronous mail delivery, scheduled retries, delivery history, and bounce diagnostics;
- approved mail templates and attachments;
- additional same-origin request hardening only if deployment expands beyond trusted LAN.

## Deferred product domains

- participant profiles;
- routes and GPX;
- warehouse balances, issue workflow, and participant distribution;
- procurement prices, shops, stock balances, and external aggregators.

## Configuration export/import debt

- versioned validated archive;
- protected-value exclusion from unencrypted exports;
- approved encryption, integrity, preview, and rollback design.

## Product Owner decisions required for later releases

- which post-release debt slice follows TH-0101;
- whether invitation lifecycle/delivery-result audit should be selected next;
- whether preference weighting beyond approved generation modes belongs in a later release;
- mandatory Recipe metadata for a later release;
- encrypted settings archive format.

No deferred item is active merely because it appears in this document. Work starts only through an explicitly selected task.
