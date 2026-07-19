# TourHub Project Status

Status date: 2026-07-19

## Current phase

TourHub v0.1.0 is release-ready at Alembic head `h10021`.

The approved first local single-club release is feature frozen through TH-0092 / PR #102. TH-0093 adds final migration and release readiness. TH-0095 delivers the routed responsive Project workspace. TH-0097 adds safe shared Product catalogue editing. TH-0098 / PR #108 synchronizes every newly published CLUB Recipe into the Dish catalogue while keeping generator classification explicitly human-owned.

## Verified baseline

- Previous Alembic revision: `h10020`.
- Accepted and final Alembic head: `h10021`.
- PR #84 through PR #89 delivered typed System Settings (`h10008`–`h10013`).
- PR #90 through PR #95 delivered Access, roles, users, preparation authorization, mail, and multi-user readiness (`h10014`–`h10016`).
- PR #96 through PR #98 delivered Recipe ownership, moderation, Dish variants, generation modes, and assignment Recipe snapshots (`h10017`–`h10019`).
- PR #99 delivered actor-aware append-only audit events (`h10020`).
- PR #100 delivered complete consolidated Russian PDF/XLSX exports.
- PR #101 delivered centralized alcohol policy and existing-record archival (`h10021`).
- PR #102 accepted and feature froze the first-release scope.
- PR #103 verified final migration/release readiness and created `v0.1.0`.
- PR #105 replaced the long Project landing page with routed Overview, Menu, Shopping, Equipment, and Documents work areas without a migration.
- PR #107 added Product catalogue editing while preserving Product IDs, Recipe relationships, and RecipeComponent quantities.
- PR #108 adds transaction-owned published Recipe-to-Dish synchronization and explicit generator readiness states without a migration.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Accepted first-release baseline

- complete guided Project preparation through shopping, equipment, readiness, consolidated Russian PDF/XLSX, compatibility files, and coordinated ZIP;
- installation, update, backup, restore, recovery, release images, health checks, same-origin API proxy, LAN access, and restart persistence;
- responsive typed System Settings through ADR-014;
- invitation-only Access, server-owned sessions, users, roles, preparation authorization, SMTP delivery, and multi-user operational behavior through ADR-015–ADR-019;
- Recipe ownership, lifecycle, moderation, Dish variants, generation modes, and persisted assignment Recipe snapshots through ADR-020–ADR-022;
- append-only actor-aware audit foundation through ADR-023;
- complete consolidated Project export contract through ADR-024;
- one centralized no-exceptions alcohol policy, HTTP 422 boundary, archive markers, historical preservation, and reversible `h10021` migration through ADR-025;
- machine-readable Product Acceptance and Release Readiness evidence;
- explicit deferred non-blocking scope and feature-freeze rules.

## Final release evidence

- PostgreSQL 18 passes `h10020 → h10021 → h10020 → h10021` against the real historical schema with representative data.
- Alembic retains exactly one head and finishes at `h10021`.
- `docs/DEPLOYMENT_CHECKLIST.md` defines prerequisites, secrets, backup, upgrade, health, LAN, product smoke, rollback, and operator sign-off.
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, and Docker Release Runtime run on both pull requests and pushes to `main`.
- Final Release Readiness preserves immutable tag `v0.1.0` at its recorded release commit.
- Production rollback remains backup-based; Alembic downgrade is verification evidence rather than the normal operator rollback mechanism.

## Delivered post-release improvements

### Project workspace UX — TH-0095

- compact Overview and routed Menu, Shopping, Equipment, and Documents sections;
- temporary navigation drawer below desktop width;
- readable tablet/mobile checklist controls;
- no horizontal overflow at 360 px, 831 px, and 1280 px.

### Product catalogue editing — TH-0097

- active Products can be updated through `PUT /products/{product_id}`;
- Product IDs and Recipe relationships remain unchanged;
- changing the Product catalogue unit does not convert RecipeComponent amount/unit values;
- the Recipe component dialog exposes `Изменить продукт` with a shared-impact warning.

### Published Recipe Dish synchronization — TH-0098

- publication and Dish synchronization share one SQLAlchemy transaction and rollback boundary;
- a Recipe already attached to any Dish is not duplicated;
- an active exact-name Dish receives the Recipe as the next variant while keeping its default and roles;
- otherwise publication creates one active Dish with the Recipe as default and only variant;
- newly created Dishes have zero roles and show `Не настроено для генератора`;
- the direct `Настроить генератор` action opens the existing role editor;
- after explicit role assignment the Dish shows `Готово для генератора` and participates in readiness coverage;
- no role, meal type, or repeatability value is inferred automatically;
- Backend transaction tests and focused real-Chrome acceptance cover the workflow.

## Deferred non-blocking debt

- explicit audit instrumentation for project/menu, settings, mail, invitations, catalogue/import, shopping, equipment, and document-generation writes;
- ownership-aware import UX, Product/Dish archive-management UI, and reviewed policy-vocabulary evolution;
- moderation notifications, session administration, account recovery, asynchronous delivery, and bounce handling;
- richer Recipe metadata, per-meal Recipe switching, and preference weights;
- audit export, retention UI, SIEM, undo, and replay;
- participant profiles, routes/GPX, warehouse balances, procurement prices, and external aggregators;
- scheduled/emailed documents, signatures, and encrypted configuration archives.

## Next work

No additional post-release capability is selected automatically after TH-0098. The next task requires an explicit Product Owner decision and must preserve the released architecture, immutable tag, and Alembic head unless separately approved.
