# TourHub Project Status

Status date: 2026-07-17

## Current phase

The guided single-club preparation baseline, operator path, production-like Docker runtime, product completeness audit, and System Settings through future invitation policy are complete. Draft PR #89 implements the final pre-access System Settings boundary: typed non-sensitive mail configuration and external environment-secret status without delivery.

## Verified baseline

- `main`: `d79172fef861c030ff2d9e5367cf86329068b460` — merged PR #88.
- `main` Alembic head: `h10012`.
- PR #84 merged as `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a`.
- PR #85 merged as `0e4e376470072e9475a31504faeb46e8b5a68364`.
- PR #86 merged as `18d5c9637e2e692b630009167dd622ee40ee2747`.
- PR #87 merged as `717d6f22d58e86a952edad501f05d3c67d8c0bf4`.
- PR #88 passed Quality #631, Document Quality #255, Guided Release Acceptance #206, Operator Docs #192, and Docker Release Runtime #187 before merge.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented on main

- complete guided preparation from project creation through Russian purchase/equipment documents and ZIP;
- persisted shopping, packaging, checklist, equipment, overrides, recalculation, and reload-safe readiness;
- installation, update, backup, restore, recovery, immutable release images, health checks, API proxy, and restart persistence;
- responsive `/settings` with independent typed ownership through ADR-014;
- `ClubSettings` (`h10008`), `AppearanceSettings` (`h10009`), `DocumentAppearanceSettings` (`h10010`), `ModuleSettings` (`h10011`), and `InvitationSettings` (`h10012`);
- dynamic organization appearance, isolated previews, one immutable club/document snapshot, module visibility/dependency locks, and future invitation policy;
- direct routes/APIs remain available when modules are hidden because visibility is not authorization;
- invitation policy creates no users, tokens, sessions, mail, or functional invitation records;
- optimistic versions, PostgreSQL row locks, HTTP 409 conflicts, and safe local-admin history.

## Draft PR #89 — informative mail boundary

Backend and persistence:

- additive Alembic `h10013` creates independent singleton `mail_settings` persistence;
- stores only SMTP host, port, connection mode, optional username, sender identity, optional Reply-To, optional test recipient, timeout, retries, version, and timestamp;
- validates DNS/IP/localhost hosts, email addresses, ranges, and plain/STARTTLS/TLS modes;
- rejects unknown request fields before service execution;
- uses versioned row-locked updates, HTTP 409 conflicts, and safe field-name-only history.

Security boundary:

- the external value is supplied only through `TOURHUB_SMTP_SECRET`;
- normal APIs return only its environment source/name and configured boolean;
- PostgreSQL, update requests, normal responses, UI inputs, logs, and focused history contain no value;
- delivery and test delivery are hard-disabled until identity exists.

Frontend and operations:

- the `Почта` placeholder becomes a responsive editor for non-sensitive values;
- status, reset, cancel, save, conflict, version, history, and disabled test action are shown in Russian;
- development/release Compose pass the optional environment value to Backend;
- installation docs state that current behavior is status-only and does not connect or send.

## Remaining sequence

1. Access foundation and functional invitations.
2. Working SMTP delivery connected to identity and the fixed Russian test message.
3. Recipe ownership/lifecycle, central alcohol policy, actor-aware audit, consolidated exports, product acceptance, then feature freeze.

## Quality debt

- finish exact-head validation and review for PR #89;
- active catalogue/import acceptance;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
