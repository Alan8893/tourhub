# TourHub Project Status

Status date: 2026-07-18

## Current phase

The guided single-club preparation baseline, production-like runtime, Product Completeness Audit, complete System Settings foundation, and first-release Access foundation are merged. Draft PR #94 implements working SMTP delivery, a fixed Russian test message, and automatic invitation delivery with a manual-link fallback.

## Verified baseline

- `main`: `21a66a2caae4e52f8e1a87bd242666703c4bc296` — merged PR #93.
- `main` Alembic head: `h10016`.
- PR #84 through PR #89 delivered the typed System Settings foundation (`h10008`–`h10013`).
- PR #90 merged as `26c4d4eb9246de44579451fe3d6e7bd631538324` (`h10014`).
- PR #91 merged as `2348870864efa1da20547c1a6564dc5f9b6488ef` (`h10015`).
- PR #92 merged as `257d82a9f4f7e47095f8e96635bf62a9ed14e722` (`h10016`).
- PR #93 merged as `21a66a2caae4e52f8e1a87bd242666703c4bc296` with no migration.
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
- public onboarding and invitation acceptance; Administrator-only settings, invitation management, and user administration.

## Draft PR #94 — Working mail delivery

Backend:

- standard-library SMTP transport supports plain, STARTTLS, and implicit TLS;
- optional authentication reads the deployment-managed value from `TOURHUB_SMTP_SECRET` only when a username is configured;
- connection check performs no message delivery;
- the fixed Russian test message uses the saved test recipient and sender metadata;
- timeout and retry count come from typed Mail Settings;
- invitation create/reissue commits first and then performs best-effort automatic delivery;
- a failed or unavailable delivery never rolls back the invitation and the one-time manual link remains available;
- operation responses contain only safe status, message, attempt count, and optional recipient;
- no migration is required; Alembic remains at `h10016`.

Frontend and validation:

- Mail Settings exposes save, connection check, and test-message actions;
- checks use the saved server version, not unsaved form values;
- invitation UI shows sent/unavailable/failed status and always retains copy-link fallback;
- no secret input is rendered;
- fake-SMTP service tests cover plain, STARTTLS, TLS, authentication, retry, and safe failure;
- Chrome acceptance covers mail actions, invitation delivery status, manual fallback, and mobile containment.

## Remaining sequence

1. Recipe ownership/lifecycle and role-specific publication/moderation.
2. Central alcohol policy.
3. Actor-aware identity and consolidated audit.
4. Consolidated exports, product acceptance, then feature freeze.

## Quality debt

- finish exact-head validation and review for PR #94;
- active catalogue/import acceptance;
- session administration and account recovery remain deferred Access operations;
- asynchronous delivery queues and bounce handling remain deferred;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
