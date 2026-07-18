# TourHub Project Status

Status date: 2026-07-18

## Current phase

The guided single-club preparation baseline, production-like runtime, Product Completeness Audit, complete System Settings foundation, first-release Access and mail foundation, multi-user operational readiness, Recipe ownership, publication/moderation, and Dish Recipe variants with project generation modes are complete through TH-0088 / PR #98.

The next release-blocking capability is the centralized alcohol prohibition across Product, Recipe, and CSV import paths.

## Verified baseline

- Alembic head: `h10019`.
- PR #84 through PR #89 delivered the typed System Settings foundation (`h10008`–`h10013`).
- PR #90 through PR #93 delivered bootstrap, sessions, invitations, users, roles, and preparation authorization (`h10014`–`h10016`).
- PR #94 delivered working SMTP invitation delivery with no migration.
- PR #95 delivered multi-user operational readiness with no migration.
- PR #96 delivered Recipe CLUB/PERSONAL ownership (`h10017`).
- PR #97 delivered Recipe publication and moderation (`h10018`).
- TH-0088 / PR #98 delivers ordered Dish Recipe variants, project generation modes, and persisted assignment Recipe snapshots (`h10019`).
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
- one ordered Recipe variant set per Dish with one required published CLUB default;
- project modes `club_only`, `club_and_personal`, and `personal_preferred`;
- actor-aware PERSONAL variant visibility without exposing another user's recipes;
- exact selected Recipe persisted on MealSlotDish and compatibility MealPlanItem;
- regeneration preserves manually edited slots and their selected Recipe;
- shopping and equipment calculations use persisted assignment Recipes rather than the mutable Dish default;
- responsive Dish variant editor, project mode selector, and selected-Recipe presentation in the meal plan.

## Remaining sequence

1. Central alcohol prohibition.
2. Actor-aware identity and consolidated audit, including immutable moderation history.
3. Consolidated export completeness.
4. Product acceptance and feature freeze.
5. Final migration cycle and release gates.

## Quality debt

- active catalogue/import acceptance;
- ownership-aware import UX beyond trusted CLUB catalogue imports;
- full moderation history beyond the latest decision;
- moderation notifications remain deferred;
- session administration and account recovery remain deferred Access operations;
- asynchronous delivery queues and bounce handling remain deferred;
- per-meal manual Recipe switching and preference weights beyond the approved three modes remain deferred;
- final PostgreSQL downgrade/re-upgrade cycle starts only after feature freeze;
- final release workflow and deployment checklist remain pending.
