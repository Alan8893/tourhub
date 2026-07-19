# TourHub Project Status

Status date: 2026-07-19

## Current phase

TourHub v0.1.0 is release-ready at Alembic head `h10021`.

The approved first local single-club release is feature frozen through TH-0092 / PR #102. TH-0093 adds final migration and release readiness. TH-0095 delivers the routed responsive Project workspace. TH-0097 / PR #107 adds safe shared Product catalogue editing without changing RecipeComponent quantities, persistence boundaries, or the released database head.

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
- PR #107 adds Product catalogue editing from the Recipe component workflow while preserving Product IDs and existing Recipe relationships.
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
- Final Release Readiness creates lightweight tag `v0.1.0` only after those workflows pass on the exact merged `main` SHA.
- Production rollback remains backup-based; Alembic downgrade is verification evidence rather than the normal operator rollback mechanism.

## Post-release Project workspace UX

- `/projects/:id` is a compact Overview rather than one long page.
- Menu, Shopping, Equipment, and Documents have stable section URLs.
- Project Recipe generation mode is edited in a settings dialog.
- Shopping uses separate calculation/packing and checklist tabs.
- The global sidebar becomes a temporary drawer below the desktop breakpoint, including the 831 px viewport reported by the Product Owner.
- Checklist controls remain readable on tablet/mobile widths.
- Browser acceptance verifies no horizontal overflow at 360 px, 831 px, and 1280 px.
- Existing preparation, reload persistence, module visibility, and complete-package download behavior remain intact.

## Post-release Product catalogue editing

- active Products can be updated through `PUT /products/{product_id}`;
- name, category, catalogue unit, and package size use the same validation and central alcohol policy as creation;
- Product IDs and Recipe relationships remain unchanged;
- changing the Product catalogue unit does not convert or rewrite RecipeComponent amount/unit values;
- the Recipe component dialog exposes `Изменить продукт` next to the selected Product;
- the edit dialog warns that shared changes affect every referencing Recipe;
- Product and Recipe queries refresh after save;
- Backend API and real-Chrome acceptance cover update, duplicate, prohibited, missing, shared-reference, and responsive behavior.

## Deferred non-blocking debt

- explicit audit instrumentation for project/menu, settings, mail, invitations, catalogue/import, shopping, equipment, and document-generation writes;
- ownership-aware import UX, Product/Dish archive-management UI, and reviewed policy-vocabulary evolution;
- automatic published Recipe-to-Dish synchronization and generator-readiness marking until TH-0098 is delivered;
- moderation notifications, session administration, account recovery, asynchronous delivery, and bounce handling;
- richer Recipe metadata, per-meal Recipe switching, and preference weights;
- audit export, retention UI, SIEM, undo, and replay;
- participant profiles, routes/GPX, warehouse balances, procurement prices, and external aggregators;
- scheduled/emailed documents, signatures, and encrypted configuration archives.

## Next work

TH-0098 Published Recipe Dish Synchronization is the next Product Owner-approved task after TH-0097 merges. It must remain a separate transactionally tested PR and must not infer generator roles automatically.
