# TourHub Project Status

Status date: 2026-07-17

## Current phase

The guided single-club preparation baseline, operator path, production-like Docker runtime, product completeness audit, club/site/document settings, and module visibility are complete. Draft PR #88 implements typed future invitation policy without creating operational users or invitations.

## Verified baseline

- `main`: `717d6f22d58e86a952edad501f05d3c67d8c0bf4` — merged PR #87.
- `main` Alembic head: `h10011`.
- PR #84 merged as `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a`.
- PR #85 merged as `0e4e376470072e9475a31504faeb46e8b5a68364`.
- PR #86 merged as `18d5c9637e2e692b630009167dd622ee40ee2747`.
- PR #87 passed Quality #604, Document Quality #229, Guided Release Acceptance #180, Operator Docs #166, and Docker Release Runtime #161 before merge.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented on main

- complete guided preparation from project creation through Russian purchase/equipment documents and ZIP;
- persisted shopping, packaging, checklist, equipment, overrides, recalculation, and reload-safe readiness;
- installation, update, backup, restore, recovery, immutable release images, health checks, API proxy, and restart persistence;
- responsive `/settings` with independent typed ownership through ADR-014;
- `ClubSettings` (`h10008`), `AppearanceSettings` (`h10009`), `DocumentAppearanceSettings` (`h10010`), and `ModuleSettings` (`h10011`);
- dynamic organization appearance, isolated previews, and one immutable club/document snapshot per generation request;
- module navigation/workspace visibility with backend/database dependency locks;
- direct routes and APIs remain available because visibility is not authorization;
- optimistic versions, PostgreSQL row locks, HTTP 409 conflicts, and safe local-admin history.

## Draft PR #88 — invitation policy

- additive Alembic `h10012` creates singleton `invitation_settings` persistence;
- typed expiry days, safe default role, allowed domains, resend policy, active limit, mandatory administrator-only rule, and email confirmation;
- default role is Instructor or Verified Instructor, never Administrator;
- domains are normalized to lowercase ASCII IDNA, deduplicated, sorted, and validated without `@`, schemes, paths, or ports;
- an empty domain list means any domain;
- stale updates return HTTP 409 and history stores changed field names only;
- the responsive Russian editor exposes reset, cancel, save, conflict, version, normalization, and history states;
- the UI explicitly states that users, invitation records, tokens, email delivery, and acceptance are not implemented.

## Remaining sequence

1. Informative mail configuration and external/write-only secret boundary.
2. Access foundation and functional invitations.
3. Working SMTP delivery after identity exists.
4. Recipe ownership/lifecycle, central alcohol policy, actor-aware audit, consolidated exports, product acceptance, then feature freeze.

## Quality debt

- finish exact-head validation and review for PR #88;
- active catalogue/import acceptance;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
