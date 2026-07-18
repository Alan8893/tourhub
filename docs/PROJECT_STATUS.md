# TourHub Project Status

Status date: 2026-07-18

## Current phase

The guided single-club preparation baseline, production-like runtime, Product Completeness Audit, complete System Settings foundation, first-release Access foundation, working SMTP delivery, and multi-user operational readiness are complete through PR #95. Draft PR #96 implements the first Recipe Ownership and Lifecycle slice: explicit CLUB/PERSONAL ownership and role-aware editing.

## Verified baseline

- `main`: `82315e0ff9520b52ae5244f69bc05d4a5d0db5b3` — merged PR #95.
- `main` Alembic head: `h10016`.
- PR #84 through PR #89 delivered the typed System Settings foundation (`h10008`–`h10013`).
- PR #90 merged as `26c4d4eb9246de44579451fe3d6e7bd631538324` (`h10014`).
- PR #91 merged as `2348870864efa1da20547c1a6564dc5f9b6488ef` (`h10015`).
- PR #92 merged as `257d82a9f4f7e47095f8e96635bf62a9ed14e722` (`h10016`).
- PR #93 merged as `21a66a2caae4e52f8e1a87bd242666703c4bc296` with no migration.
- PR #94 merged as `3c51d4c1d0bb0bd96d23a1f4ace0947ae48e9101` with no migration.
- PR #95 merged as `82315e0ff9520b52ae5244f69bc05d4a5d0db5b3`; exact implementation head `8570670209566f6860b71c0173557bb71bf6fe00` passed Quality #843, Document Quality #460, Guided Release Acceptance #411, Operator Docs #397, and Docker Release Runtime #392.
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
- working SMTP delivery and invitation fallback through ADR-019;
- multiple independent sessions, current-role propagation, complete deactivation revocation, centralized frontend 401 handling, exact route return, and visible current role through TH-0085.

## Draft PR #96 — Recipe Ownership Foundation

- Recipe gains `scope` (`club` or `personal`) and nullable `owner_user_id` through ADR-020;
- migration `h10017` preserves every existing Recipe as CLUB with no owner;
- interactive creation produces a PERSONAL Recipe owned by the current authenticated user;
- Administrator may view all recipes; other roles see CLUB plus their own PERSONAL recipes;
- Instructor edits owned PERSONAL recipes only;
- Verified Instructor edits owned PERSONAL recipes and CLUB recipes;
- Administrator edits all recipes and remains the only role allowed to permanently delete;
- the same policy protects components, notes, and equipment requirements;
- API responses expose safe owner identity and current-actor capabilities;
- frontend labels club/personal ownership and follows server-projected capabilities.

## Remaining sequence

1. Recipe submission, review, publication, rejection, and moderation history.
2. Dish recipe variants and generation modes.
3. Central alcohol policy.
4. Actor-aware identity and consolidated audit.
5. Consolidated exports, product acceptance, then feature freeze.

## Quality debt

- active catalogue/import acceptance;
- session administration and account recovery remain deferred Access operations;
- asynchronous delivery queues and bounce handling remain deferred;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
