# TourHub Project Status

Status date: 2026-07-18

## Current phase

The guided single-club preparation baseline, production-like runtime, Product Completeness Audit, complete System Settings foundation, first-release Access foundation, and working SMTP delivery are merged. TH-0085 hardens the existing multi-user runtime before recipe ownership and moderation begin.

## Verified baseline

- `main`: `3c51d4c1d0bb0bd96d23a1f4ace0947ae48e9101` — merged PR #94.
- `main` Alembic head: `h10016`.
- PR #84 through PR #89 delivered the typed System Settings foundation (`h10008`–`h10013`).
- PR #90 merged as `26c4d4eb9246de44579451fe3d6e7bd631538324` (`h10014`).
- PR #91 merged as `2348870864efa1da20547c1a6564dc5f9b6488ef` (`h10015`).
- PR #92 merged as `257d82a9f4f7e47095f8e96635bf62a9ed14e722` (`h10016`).
- PR #93 merged as `21a66a2caae4e52f8e1a87bd242666703c4bc296` with no migration.
- PR #94 merged as `3c51d4c1d0bb0bd96d23a1f4ace0947ae48e9101` with no migration.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented on main

- complete guided preparation through Russian purchase/equipment documents and ZIP;
- persisted shopping, packaging, checklist, equipment, overrides, recalculation, and reload-safe readiness;
- installation, update, backup, restore, recovery, release images, health checks, API proxy, and restart persistence;
- responsive typed System Settings through ADR-014;
- one-time Administrator bootstrap, server sessions, login/logout/current-user, and Administrator-only settings through ADR-015;
- functional invitation lifecycle and invited-user sign-in through ADR-016;
- user list, role/activity administration, optimistic versions, and final-active-Administrator protection through ADR-017;
- authenticated preparation routes and APIs for all three approved active roles through ADR-018;
- public onboarding and invitation acceptance; Administrator-only settings, invitation management, and user administration;
- working plain/STARTTLS/TLS SMTP delivery, connection check, fixed Russian test message, and best-effort invitation delivery with manual fallback through ADR-019.

## Active TH-0085 — Multi-user operational readiness

Backend:

- focused integration verifies two independent sessions for one user;
- role changes must be visible from both sessions on the next request;
- deactivation must revoke all active sessions for that user;
- existing optimistic conflicts and final-active-Administrator protection remain unchanged.

Frontend:

- protected HTTP 401 responses invalidate stale local identity centrally;
- route guards return the user to the exact path, query, and hash after sign-in;
- explicit logout also preserves the current destination;
- the header displays the current user role;
- browser acceptance covers server-side session revocation and recovery.

No migration is required; Alembic remains at `h10016`.

## Remaining sequence

1. Recipe ownership/lifecycle and role-specific publication/moderation.
2. Central alcohol policy.
3. Actor-aware identity and consolidated audit.
4. Consolidated exports, product acceptance, then feature freeze.

## Quality debt

- complete exact-head validation and review for TH-0085;
- active catalogue/import acceptance;
- session administration and account recovery remain deferred Access operations;
- asynchronous delivery queues and bounce handling remain deferred;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
