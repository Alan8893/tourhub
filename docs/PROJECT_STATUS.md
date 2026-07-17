# TourHub Project Status

Status date: 2026-07-18

## Current phase

The guided single-club preparation baseline, production-like runtime, product completeness audit, complete System Settings foundation, and first Access slice are merged. Draft PR #91 implements functional one-time invitations and creation of Instructor or Verified Instructor users without depending on SMTP delivery.

## Verified baseline

- `main`: `26c4d4eb9246de44579451fe3d6e7bd631538324` — merged PR #90.
- `main` Alembic head: `h10014`.
- PR #84 merged as `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a`.
- PR #85 merged as `0e4e376470072e9475a31504faeb46e8b5a68364`.
- PR #86 merged as `18d5c9637e2e692b630009167dd622ee40ee2747`.
- PR #87 merged as `717d6f22d58e86a952edad501f05d3c67d8c0bf4`.
- PR #88 merged as `d79172fef861c030ff2d9e5367cf86329068b460`.
- PR #89 merged as `bff7950e3542b719983f2a09b61b9a901fbaca64`.
- PR #90 passed Quality #716, Document Quality #338, Guided Release Acceptance #289, Operator Docs #275, and Docker Release Runtime #270 before merge.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented on main

- complete guided preparation from project creation through Russian purchase/equipment documents and ZIP;
- persisted shopping, packaging, checklist, equipment, overrides, recalculation, and reload-safe readiness;
- installation, update, backup, restore, recovery, immutable release images, health checks, API proxy, and restart persistence;
- responsive `/settings` with independent typed ownership through ADR-014;
- settings migrations `h10008` through `h10013` for club, site appearance, document appearance, modules, invitation policy, and mail metadata;
- one immutable club/document snapshot per generation request;
- module visibility remains presentation-only;
- one-time Administrator bootstrap, scrypt password hashing, server-owned sessions, login/logout/current-user, and System Settings authorization through ADR-015 and `h10014`;
- session cookies contain opaque random values while PostgreSQL stores only token hashes;
- mail metadata does not connect to SMTP or send messages;
- optimistic settings versions, PostgreSQL row locks, HTTP 409 conflicts, and safe focused history.

## Draft PR #91 — Functional invitation lifecycle

Backend and persistence:

- additive Alembic `h10015` creates typed invitation rows;
- Administrator endpoints create, list, reissue, and revoke invitations;
- raw one-time codes are returned only in immediate create/reissue responses;
- PostgreSQL stores only SHA-256 code hashes, never reusable raw links;
- Backend consumes `InvitationSettings` for allowed domains, safe roles, expiry, active limits, and reissue policy;
- public inspection exposes only bound email, role, and expiry after code validation;
- acceptance row-locks the invitation, creates one active user, consumes the invitation, and creates the first session atomically;
- expired, revoked, consumed, superseded, and unknown links are rejected.

Frontend:

- the invitation settings section now separates active policy from operational link management;
- Administrators create, copy, reissue, and revoke links;
- `/accept-invitation` validates the link before collecting name and password;
- successful acceptance signs the new user into TourHub;
- desktop and mobile layouts remain responsive;
- links are delivered manually until working SMTP delivery exists.

## Remaining sequence

1. User administration, activation/deactivation, and explicit role changes.
2. Broader guarded routes and backend authorization for preparation mutations.
3. Actor-aware identity in settings history and the consolidated audit log.
4. Working SMTP delivery connected to identity and the fixed Russian test message.
5. Recipe ownership/lifecycle, central alcohol policy, consolidated exports, product acceptance, then feature freeze.

## Quality debt

- finish exact-head validation and review for PR #91;
- add broader end-to-end acceptance when user administration and authorization matrix exist;
- active catalogue/import acceptance;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
