# TourHub Project Status

Status date: 2026-07-18

## Current phase

The guided single-club preparation baseline, production-like runtime, Product Completeness Audit, complete System Settings foundation, first-release Access foundation, working SMTP delivery, and multi-user operational readiness are complete through PR #95. The next product capability is recipe ownership and lifecycle.

## Verified baseline

- Alembic head: `h10016`.
- PR #84 through PR #89 delivered the typed System Settings foundation (`h10008`–`h10013`).
- PR #90 merged as `26c4d4eb9246de44579451fe3d6e7bd631538324` (`h10014`).
- PR #91 merged as `2348870864efa1da20547c1a6564dc5f9b6488ef` (`h10015`).
- PR #92 merged as `257d82a9f4f7e47095f8e96635bf62a9ed14e722` (`h10016`).
- PR #93 merged as `21a66a2caae4e52f8e1a87bd242666703c4bc296` with no migration.
- PR #94 merged as `3c51d4c1d0bb0bd96d23a1f4ace0947ae48e9101` with no migration.
- PR #95 implementation head `4879e6dc701550935eb4d173e5098de85d264fd5` passed Quality #835, Document Quality #452, Guided Release Acceptance #403, Operator Docs #389, and Docker Release Runtime #384.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented baseline

- complete guided preparation through Russian purchase/equipment documents and ZIP;
- persisted shopping, packaging, checklist, equipment, overrides, recalculation, and reload-safe readiness;
- installation, update, backup, restore, recovery, release images, health checks, API proxy, and restart persistence;
- responsive typed System Settings through ADR-014;
- one-time Administrator bootstrap, server sessions, login/logout/current-user, and Administrator-only settings through ADR-015;
- functional invitation lifecycle and invited-user sign-in through ADR-016;
- user list, role/activity administration, optimistic versions, and final-active-Administrator protection through ADR-017;
- authenticated preparation routes and APIs for all three approved active roles through ADR-018;
- public onboarding and invitation acceptance; Administrator-only settings, invitation management, and user administration;
- working plain/STARTTLS/TLS SMTP delivery, connection check, fixed Russian test message, and best-effort invitation delivery with manual fallback through ADR-019;
- multiple independent sessions per user, current-role propagation on each request, and complete session revocation on deactivation;
- centralized frontend handling for protected HTTP 401 responses;
- exact route return through sign-in and explicit logout;
- visible current user role in the common application header.

No migration was required for PR #93 through PR #95; Alembic remains at `h10016`.

## Remaining sequence

1. Recipe ownership/lifecycle and role-specific publication/moderation.
2. Central alcohol policy.
3. Actor-aware identity and consolidated audit.
4. Consolidated exports, product acceptance, then feature freeze.

## Quality debt

- active catalogue/import acceptance;
- session administration and account recovery remain deferred Access operations;
- asynchronous delivery queues and bounce handling remain deferred;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
