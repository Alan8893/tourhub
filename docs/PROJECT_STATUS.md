# TourHub Project Status

Status date: 2026-07-19

## Current phase

The guided single-club preparation baseline, production-like runtime, Product Completeness Audit, complete System Settings foundation, first-release Access and mail foundation, multi-user operational readiness, Recipe ownership/publication/moderation, Dish Recipe variants with generation modes, Actor-Aware Audit Foundation, and consolidated Russian Project exports are complete through TH-0090 / PR #100.

The next release-blocking capability is the centralized alcohol prohibition across Product, Recipe, Dish, and CSV import paths immediately before product acceptance.

## Verified baseline

- Alembic head: `h10020`.
- PR #84 through PR #89 delivered the typed System Settings foundation (`h10008`–`h10013`).
- PR #90 through PR #93 delivered bootstrap, sessions, invitations, users, roles, and preparation authorization (`h10014`–`h10016`).
- PR #94 delivered working SMTP invitation delivery with no migration.
- PR #95 delivered multi-user operational readiness with no migration.
- PR #96 delivered Recipe CLUB/PERSONAL ownership (`h10017`).
- PR #97 delivered Recipe publication and moderation (`h10018`).
- PR #98 delivered ordered Dish Recipe variants, project generation modes, and persisted assignment Recipe snapshots (`h10019`).
- PR #99 delivered actor-aware append-only audit events (`h10020`).
- TH-0090 / PR #100 delivers complete consolidated Russian PDF/XLSX exports with no migration.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented baseline

- complete guided preparation through Russian purchase/equipment documents, complete Project PDF/XLSX, and coordinated ZIP;
- persisted shopping, packaging, checklist, equipment, overrides, recalculation, and reload-safe readiness;
- installation, update, backup, restore, recovery, release images, health checks, API proxy, and restart persistence;
- responsive typed System Settings through ADR-014;
- invitation-only Access, explicit roles, user administration, and preparation authorization through ADR-015–ADR-018;
- working SMTP delivery and invitation fallback through ADR-019;
- multiple sessions, current-role propagation, deactivation revocation, centralized protected-401 handling, exact route return, and visible current role through TH-0085;
- Recipe CLUB/PERSONAL ownership and role-aware nested authorization through ADR-020 and `h10017`;
- Recipe lifecycle `draft → submitted → published|rejected`, row-locked moderation, rejection feedback, resubmission, and attribution through ADR-021 and `h10018`;
- ordered Recipe variants per Dish, three project generation modes, persisted assignment Recipe snapshots, and assignment-based shopping/equipment calculations through ADR-022 and `h10019`;
- append-only AuditEvent records with actor snapshots, safe bounded change payloads, semantic user-access/Recipe moderation events, Administrator filtering, and responsive audit UI through ADR-023 and `h10020`;
- one consolidated Project export DTO using persisted MealSlotDish Recipe snapshots, purchase/checklist state, equipment, warnings, comments, and one immutable brand snapshot;
- complete landscape Russian PDF sections for Project parameters, menu, loadout, shopping, equipment, warnings, and comments;
- complete XLSX sheets `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование`;
- primary complete-download controls plus preserved compatibility purchase/equipment endpoints and ZIP artifacts through ADR-024.

## Remaining sequence

1. Central alcohol prohibition.
2. Product acceptance and feature freeze.
3. Final migration cycle and release gates.

## Quality debt

- explicit audit instrumentation for project/menu, settings, mail, invitations, catalogue/import, shopping, equipment, and document-generation write paths;
- active catalogue/import acceptance;
- ownership-aware import UX beyond trusted CLUB catalogue imports;
- moderation notifications remain deferred;
- session administration and account recovery remain deferred Access operations;
- asynchronous delivery queues and bounce handling remain deferred;
- per-meal manual Recipe switching and preference weights beyond the approved three modes remain deferred;
- audit export, retention UI, SIEM integration, undo, and event replay remain deferred;
- final PostgreSQL downgrade/re-upgrade cycle starts only after feature freeze;
- final release workflow and deployment checklist remain pending.
