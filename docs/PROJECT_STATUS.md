# TourHub Project Status

Status date: 2026-07-18

## Current phase

The guided single-club preparation baseline, production-like runtime, product completeness audit, complete System Settings foundation, Administrator bootstrap/sessions, functional invitations, and user administration are merged. Draft PR #93 completes the first-release Access boundary by requiring an active session for all preparation routes and APIs.

## Verified baseline

- `main`: `257d82a9f4f7e47095f8e96635bf62a9ed14e722` — merged PR #92.
- `main` Alembic head: `h10016`.
- PR #84 merged as `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a`.
- PR #85 merged as `0e4e376470072e9475a31504faeb46e8b5a68364`.
- PR #86 merged as `18d5c9637e2e692b630009167dd622ee40ee2747`.
- PR #87 merged as `717d6f22d58e86a952edad501f05d3c67d8c0bf4`.
- PR #88 merged as `d79172fef861c030ff2d9e5367cf86329068b460`.
- PR #89 merged as `bff7950e3542b719983f2a09b61b9a901fbaca64`.
- PR #90 merged as `26c4d4eb9246de44579451fe3d6e7bd631538324`.
- PR #91 merged as `2348870864efa1da20547c1a6564dc5f9b6488ef`.
- PR #92 passed Quality #778, Document Quality #398, Guided Release Acceptance #349, Operator Docs #335, and Docker Release Runtime #330 before merge.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented on main

- complete guided preparation from project creation through Russian purchase/equipment documents and ZIP;
- persisted shopping, packaging, checklist, equipment, overrides, recalculation, and reload-safe readiness;
- installation, update, backup, restore, recovery, immutable release images, health checks, API proxy, and restart persistence;
- responsive `/settings` with independent typed ownership through ADR-014;
- settings migrations `h10008` through `h10013`;
- one immutable club/document snapshot per generation request;
- module visibility remains presentation-only;
- one-time Administrator bootstrap, password hashing, server-owned sessions, and System Settings authorization through ADR-015 and `h10014`;
- functional invitation lifecycle and invited-user sign-in through ADR-016 and `h10015`;
- user list, role/activity administration, optimistic versions, and final-active-Administrator protection through ADR-017 and `h10016`;
- mail metadata remains configuration-only and does not send messages.

## Draft PR #93 — Preparation authorization matrix

Backend:

- `require_preparation_access` accepts active Administrator, Instructor, and Verified Instructor roles;
- project, catalogue, import, menu, shopping, equipment, document, dish, and current recipe router groups require that dependency;
- health, auth bootstrap/login, and invitation inspect/accept stay public;
- settings, invitation management, and user administration stay Administrator-only;
- structural tests assert that every preparation endpoint carries the dependency;
- integration tests cover 401, all three active roles, inactive users, public boundaries, and preserved 403 responses.

Frontend and runtime:

- one `RequireAuthenticated` guard wraps the full `AppLayout` tree;
- signed-out users are redirected to `/login` with the requested path preserved;
- `/login` and `/accept-invitation` remain public;
- `/settings` retains the additional Administrator guard;
- Chrome acceptance verifies redirect, bootstrap return, settings navigation, logout/login return, and mobile containment;
- guided-release and Docker runtime smoke now authenticate before exercising preparation flows;
- no new migration is required; Alembic remains at `h10016`.

## Remaining sequence

1. Working mail delivery connected to invitations and the fixed Russian test message.
2. Recipe ownership/lifecycle and role-specific publication/moderation.
3. Central alcohol policy.
4. Actor-aware identity and consolidated audit.
5. Consolidated exports, product acceptance, then feature freeze.

## Quality debt

- finish exact-head validation and review for PR #93;
- active catalogue/import acceptance;
- session administration and account recovery remain deferred Access operations;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
