# TourHub Project Status

Status date: 2026-07-19

## Current phase

The approved first local single-club release is feature frozen through TH-0092 / PR #102.

Product Acceptance passed the machine-readable manifest gate, selected real Backend API/migration scenarios, six critical Chrome scenarios, and the existing exact-head repository workflows. The only remaining release-blocking phase is Final Migration and Release Readiness.

## Verified baseline

- Alembic head: `h10021`.
- PR #84 through PR #89 delivered typed System Settings (`h10008`–`h10013`).
- PR #90 through PR #93 delivered bootstrap, sessions, invitations, users, roles, and preparation authorization (`h10014`–`h10016`).
- PR #94 delivered working SMTP invitation delivery.
- PR #95 delivered multi-user operational readiness.
- PR #96 delivered Recipe CLUB/PERSONAL ownership (`h10017`).
- PR #97 delivered Recipe publication and moderation (`h10018`).
- PR #98 delivered Dish Recipe variants, project generation modes, and persisted assignment Recipe snapshots (`h10019`).
- PR #99 delivered actor-aware append-only audit events (`h10020`).
- PR #100 delivered complete consolidated Russian PDF/XLSX exports with no migration.
- PR #101 delivered centralized alcohol policy and existing-record archival (`h10021`).
- TH-0092 / PR #102 accepts and freezes the approved first-release scope with a versioned manifest and dedicated acceptance workflow.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Accepted first-release baseline

- complete guided preparation through consolidated Russian PDF/XLSX and coordinated ZIP;
- persisted shopping, packaging, checklist, equipment, overrides, recalculation, and reload-safe readiness;
- installation, update, backup, restore, recovery, release images, health checks, API proxy, and restart persistence;
- responsive typed System Settings through ADR-014;
- invitation-only Access, roles, user administration, and preparation authorization through ADR-015–ADR-018;
- working SMTP delivery through ADR-019;
- Recipe ownership/lifecycle/moderation through ADR-020–ADR-021;
- ordered Recipe variants, three Project generation modes, persisted assignment Recipe snapshots, and assignment-based shopping/equipment through ADR-022;
- append-only actor-aware AuditEvent persistence and responsive Administrator history through ADR-023;
- complete Project PDF/XLSX export contract and compatibility package through ADR-024;
- one versioned Backend `AlcoholPolicy` with Unicode/case normalization and complete-word matching through ADR-025;
- Product, Recipe, Dish, Recipe lifecycle, and Product/Recipe CSV paths return one policy-owned HTTP 422 rejection;
- Product and Dish archive state plus policy markers preserve historical relationships while excluding prohibited records from active catalogues and new preparation selection;
- `h10021` deterministically archives prohibited Product → Recipe → default Dish records and remains reversible;
- policy-archived Recipes cannot be restored;
- machine-readable accepted capability evidence and explicit deferred non-blocking scope;
- feature-freeze rules permitting only acceptance defect fixes, security fixes, final release-readiness work, and documentation corrections.

## Remaining sequence

1. Final Migration and Release Readiness.

## Deferred non-blocking debt

- explicit audit instrumentation for project/menu, settings, mail, invitations, catalogue/import, shopping, equipment, and document-generation write paths;
- ownership-aware import UX beyond trusted CLUB catalogue imports;
- Product/Dish archive-management UI and reviewed future policy-vocabulary evolution;
- moderation notifications;
- session administration and account recovery;
- asynchronous delivery queues and bounce handling;
- per-meal manual Recipe switching and preference weights beyond the approved three modes;
- audit export, retention UI, SIEM integration, undo, and event replay;
- participant profiles, routes/GPX, warehouse balances, procurement prices, and external aggregators;
- encrypted configuration archives.

## Final release readiness

- run the final PostgreSQL previous → `h10021` → previous → `h10021` migration cycle;
- verify the production-like deployment checklist;
- add the final release workflow and create the release tag only after green exact-head gates.
