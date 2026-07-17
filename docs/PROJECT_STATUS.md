# TourHub Project Status

Status date: 2026-07-18

## Current phase

The guided single-club preparation baseline, production-like runtime, product completeness audit, and complete pre-access System Settings foundation are merged. Draft PR #90 implements the first operational Access slice: one-time Administrator bootstrap, server-owned sessions, login/logout/current-user, and Administrator protection for System Settings.

## Verified baseline

- `main`: `bff7950e3542b719983f2a09b61b9a901fbaca64` — merged PR #89.
- `main` Alembic head: `h10013`.
- PR #84 merged as `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a`.
- PR #85 merged as `0e4e376470072e9475a31504faeb46e8b5a68364`.
- PR #86 merged as `18d5c9637e2e692b630009167dd622ee40ee2747`.
- PR #87 merged as `717d6f22d58e86a952edad501f05d3c67d8c0bf4`.
- PR #88 merged as `d79172fef861c030ff2d9e5367cf86329068b460`.
- PR #89 passed Quality #660, Document Quality #283, Guided Release Acceptance #234, Operator Docs #220, and Docker Release Runtime #215 before merge.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented on main

- complete guided preparation from project creation through Russian purchase/equipment documents and ZIP;
- persisted shopping, packaging, checklist, equipment, overrides, recalculation, and reload-safe readiness;
- installation, update, backup, restore, recovery, immutable release images, health checks, API proxy, and restart persistence;
- responsive `/settings` with independent typed ownership through ADR-014;
- settings migrations `h10008` through `h10013` for club, site appearance, document appearance, modules, invitation policy, and mail metadata;
- one immutable club/document snapshot per generation request;
- module visibility remains presentation-only;
- invitation policy creates no invitation records;
- mail metadata does not connect to SMTP or send messages;
- optimistic settings versions, PostgreSQL row locks, HTTP 409 conflicts, and safe local-admin history.

## Draft PR #90 — Administrator bootstrap and authentication

Backend and persistence:

- additive Alembic `h10014` creates singleton identity state, users, and server sessions;
- bootstrap status is public, but Administrator creation is transactionally available only while no user exists;
- supported roles are Administrator, Instructor, and Verified Instructor, while bootstrap always creates Administrator;
- passwords use standard-library `scrypt` with random salt and are never returned;
- session cookies contain opaque random values; PostgreSQL stores only SHA-256 token hashes;
- sessions expire and can be revoked server-side;
- login failure is generic and does not disclose whether an account exists;
- all `/api/v1/settings/...` APIs require an authenticated Administrator.

Frontend:

- root authentication provider resolves bootstrap and current-user state;
- `/login` provides one-time bootstrap or normal login;
- `/settings` redirects unauthenticated users and rejects non-Administrators;
- the shell shows the current user and logout action;
- protected appearance/module settings reload after login and reset after logout;
- preparation routes remain available in this first slice.

## Remaining sequence

1. Functional invitation lifecycle consuming `InvitationSettings`.
2. User administration, activation, and role changes.
3. Broader guarded routes and backend authorization for preparation mutations.
4. Working SMTP delivery connected to identity and the fixed Russian test message.
5. Recipe ownership/lifecycle, central alcohol policy, actor-aware audit, consolidated exports, product acceptance, then feature freeze.

## Quality debt

- finish exact-head validation and review for PR #90;
- active catalogue/import acceptance;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
