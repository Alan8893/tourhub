# TourHub Project Status

Status date: 2026-07-18

## Current phase

The guided single-club preparation baseline, production-like runtime, product completeness audit, complete System Settings foundation, Administrator bootstrap/sessions, and functional invitation lifecycle are merged. Draft PR #92 implements Administrator-owned user administration, activation state, and explicit role changes.

## Verified baseline

- `main`: `2348870864efa1da20547c1a6564dc5f9b6488ef` — merged PR #91.
- `main` Alembic head: `h10015`.
- PR #84 merged as `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a`.
- PR #85 merged as `0e4e376470072e9475a31504faeb46e8b5a68364`.
- PR #86 merged as `18d5c9637e2e692b630009167dd622ee40ee2747`.
- PR #87 merged as `717d6f22d58e86a952edad501f05d3c67d8c0bf4`.
- PR #88 merged as `d79172fef861c030ff2d9e5367cf86329068b460`.
- PR #89 merged as `bff7950e3542b719983f2a09b61b9a901fbaca64`.
- PR #90 merged as `26c4d4eb9246de44579451fe3d6e7bd631538324`.
- PR #91 passed Quality #755, Document Quality #376, Guided Release Acceptance #327, Operator Docs #313, and Docker Release Runtime #308 before merge.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented on main

- complete guided preparation from project creation through Russian purchase/equipment documents and ZIP;
- persisted shopping, packaging, checklist, equipment, overrides, recalculation, and reload-safe readiness;
- installation, update, backup, restore, recovery, immutable release images, health checks, API proxy, and restart persistence;
- responsive `/settings` with independent typed ownership through ADR-014;
- settings migrations `h10008` through `h10013`;
- one immutable club/document snapshot per generation request;
- module visibility remains presentation-only;
- one-time Administrator bootstrap, password hashing, server-owned sessions, login/logout/current-user, and System Settings authorization through ADR-015 and `h10014`;
- functional invitation creation, repeat issue, revocation, public acceptance, invited-user creation, and initial sign-in through ADR-016 and `h10015`;
- mail metadata remains configuration-only and does not send messages.

## Draft PR #92 — User administration and roles

Backend and persistence:

- additive Alembic `h10016` adds positive optimistic versions to `User`;
- Administrator-only `/api/v1/users` list and update endpoints;
- user responses expose identity, role, activity, timestamps, version, and current-user marker without protected credential/session fields;
- updates serialize by locking the user set and require `expected_version`;
- stale updates return HTTP 409;
- the last active Administrator cannot be deactivated or demoted;
- deactivation revokes all active sessions for the target user;
- self-demotion or self-deactivation is allowed only when another active Administrator remains.

Frontend:

- System Settings adds a dedicated `Пользователи` section;
- responsive cards support role and active-state changes without wide tables;
- deactivation and Administrator demotion require explicit confirmation;
- current-account changes refresh auth state immediately;
- conflict handling reloads Backend-authoritative state;
- dedicated Chrome acceptance covers role change, deactivation, optimistic version payload, and 360 px layout.

## Remaining sequence

1. Broader guarded routes and backend authorization for preparation mutations.
2. Actor-aware identity in settings history and the consolidated audit log.
3. Session administration, account recovery, and password-reset policy.
4. Working SMTP delivery connected to invitations and the fixed Russian test message.
5. Recipe ownership/lifecycle, central alcohol policy, consolidated exports, product acceptance, then feature freeze.

## Quality debt

- finish exact-head validation and review for PR #92;
- define and implement the preparation authorization matrix;
- active catalogue/import acceptance;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
