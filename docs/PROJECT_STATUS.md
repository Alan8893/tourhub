# TourHub Project Status

Status date: 2026-07-19

## Current phase

The guided single-club preparation baseline, production-like runtime, Product Completeness Audit, complete System Settings foundation, first-release Access and mail foundation, multi-user operational readiness, Recipe ownership/publication/moderation, Dish Recipe variants with generation modes, and the Actor-Aware Audit Foundation are complete through TH-0089 / PR #99.

The next release-blocking capability is consolidated Russian export completeness. The centralized alcohol prohibition is intentionally scheduled after exports and immediately before product acceptance.

## Verified baseline

- Alembic head: `h10020`.
- PR #84 through PR #89 delivered the typed System Settings foundation (`h10008`–`h10013`).
- PR #90 through PR #93 delivered bootstrap, sessions, invitations, users, roles, and preparation authorization (`h10014`–`h10016`).
- PR #94 delivered working SMTP invitation delivery with no migration.
- PR #95 delivered multi-user operational readiness with no migration.
- PR #96 delivered Recipe CLUB/PERSONAL ownership (`h10017`).
- PR #97 delivered Recipe publication and moderation (`h10018`).
- PR #98 delivered ordered Dish Recipe variants, project generation modes, and persisted assignment Recipe snapshots (`h10019`).
- TH-0089 / PR #99 adds actor-aware append-only audit events (`h10020`).
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented baseline

- complete guided preparation through Russian purchase/equipment documents and ZIP;
- persisted shopping, packaging, checklist, equipment, overrides, recalculation, and reload-safe readiness;
- installation, update, backup, restore, recovery, release images, health checks, API proxy, and restart persistence;
- responsive typed System Settings through ADR-014;
- invitation-only Access, explicit roles, user administration, and preparation authorization through ADR-015–ADR-018;
- working SMTP delivery and invitation fallback through ADR-019;
- multiple sessions, current-role propagation, deactivation revocation, centralized protected-401 handling, exact route return, and visible current role through TH-0085;
- Recipe CLUB/PERSONAL ownership and role-aware nested authorization through ADR-020 and `h10017`;
- Recipe lifecycle `draft → submitted → published|rejected`, row-locked moderation, rejection feedback, resubmission, and attribution through ADR-021 and `h10018`;
- ordered Recipe variants per Dish, three project generation modes, persisted assignment Recipe snapshots, and assignment-based shopping/equipment calculations through ADR-022 and `h10019`;
- append-only AuditEvent records with actor identity/role snapshots, safe bounded before/after/context payloads, semantic user-access events, semantic Recipe moderation events, Administrator-only filtering, and responsive audit UI through ADR-023 and `h10020`.

## Remaining sequence

1. Consolidated export completeness.
2. Central alcohol prohibition.
3. Product acceptance and feature freeze.
4. Final migration cycle and release gates.

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
