# TourHub Current Roadmap

Status date: 2026-07-18

## Product goal

Deliver the approved local MVP for one tourist club without changing the approved architecture.

```text
Project preparation baseline
  → Production-like Docker runtime
  → Product completeness audit
  → System Settings foundation
  → Access foundation
      → First Administrator bootstrap and server sessions
      → Functional invitation lifecycle
      → User administration and explicit roles
      → Broader guarded routes and backend authorization
  → Working mail delivery
  → Recipe ownership and lifecycle
  → Central domain safety
  → Actor-aware audit
  → Consolidated Russian exports
  → Product acceptance and feature freeze
  → Final migration and release gates
```

## DONE

### Infrastructure, guided preparation, and operations

- complete guided preparation from project creation through shopping, equipment, readiness, and Russian PDF/Excel/print/ZIP outputs;
- installation, update, backup, restore, recovery, health, LAN, and production-like release Compose;
- PostgreSQL 18 and Redis internal networking, same-origin API proxy, migrations, restart persistence, and cleanup validation.

PR #77 merged as `18d4fabde3eda6c83c0c0f998e870a6f043e8dec`. PR #78 merged as `6332ef5f86973c7832e92dc1ef0a681cc4e17d1e`. PR #79 merged as `99d9c2d985b8a21c62fe148e07e08b3632ef961a`. PR #80 merged as `939828e8c335966dde2d04c5083ee7d2da07c6eb`.

### Product completeness audit

- approved product scope compared with actual implementation;
- mandatory user/domain gaps separated from later work;
- final downgrade/re-upgrade cycle moved after feature freeze;
- System Settings scheduled before access foundation.

PR #83 merged as `950a43914230f6fe4be3bf217a4e5f1b79e7265f`.

### System Settings foundation through PR #89

- PR #84: responsive `/settings`, typed club profile and images, `h10008`;
- PR #85: organization light/dark appearance, presets/import/export, `h10009`;
- PR #86: document appearance and immutable generation snapshot, `h10010`;
- PR #87: module visibility and dependency locks, `h10011`;
- PR #88: invitation policy, safe default roles and normalized domains, `h10012`;
- PR #89: non-secret mail metadata and external SMTP-value status boundary, `h10013`;
- all persisted settings sections use typed ownership, optimistic versions, PostgreSQL row locks, HTTP 409 conflicts, and safe focused history.

PR #84 merged as `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a`. PR #85 merged as `0e4e376470072e9475a31504faeb46e8b5a68364`. PR #86 merged as `18d5c9637e2e692b630009167dd622ee40ee2747`. PR #87 merged as `717d6f22d58e86a952edad501f05d3c67d8c0bf4`. PR #88 merged as `d79172fef861c030ff2d9e5367cf86329068b460`. PR #89 merged as `bff7950e3542b719983f2a09b61b9a901fbaca64`.

### Access bootstrap and sessions — PR #90

- typed `User`, `IdentityState`, and `AuthSession` persistence;
- additive Alembic `h10014` with one head;
- one-time transactional bootstrap of the first Administrator;
- memory-hard password hashing with no plaintext credential persistence;
- opaque HttpOnly SameSite session cookie with only a SHA-256 token hash stored server-side;
- bootstrap status, login, logout, current-user, expiry, and revocation;
- Administrator authorization for all System Settings APIs and guarded `/settings`;
- responsive bootstrap/login UI, current-user identity, and logout.

PR #90 passed all exact-head gates and merged as `26c4d4eb9246de44579451fe3d6e7bd631538324`.

## IN PROGRESS — TH-0081 / DRAFT PR #91

### Access: functional invitation lifecycle

- typed `Invitation` persistence and additive Alembic `h10015`;
- Administrator create/list/reissue/revoke actions;
- secure one-time codes returned only on create/reissue, with only SHA-256 hashes stored in PostgreSQL;
- Backend enforcement of allowed domains, safe roles, expiry, active limits, and repeat-issue policy from `InvitationSettings`;
- public inspection of a validated link and atomic acceptance;
- creation and immediate sign-in of Instructor or Verified Instructor users;
- expired, revoked, consumed, superseded, and unknown links cannot create users;
- responsive management UI and public `/accept-invitation` page;
- manual link delivery until working mail exists.

Scope boundary:

- no automatic SMTP delivery or message queue;
- no Administrator invitations or self-registration;
- no full user list, activation/deactivation, role editing, profile editing, or password reset;
- no broad preparation-route/API authorization yet.

## NEXT — ACCESS FOUNDATION CONTINUATION

1. user list, activation state, and explicit role management;
2. broader guarded frontend routes and backend authorization for preparation mutations;
3. actor-aware identity propagation into settings history and the later audit log;
4. session administration, cleanup, and password-reset policy.

## FOLLOW-UP PRODUCT WORK

1. **Working mail delivery** — consume `MailSettings` and the external SMTP value, verify connection, send the fixed Russian test message, and connect automatic invitation delivery.
2. **Recipe ownership and lifecycle** — CLUB/PERSONAL ownership, variants, publication, moderation, and generation modes.
3. **Central alcohol prohibition** — one backend policy across Product, Recipe, and CSV import paths.
4. **Actor-aware audit log** — safe history for project, menu, recipe, user, role, mail, and settings changes.
5. **Consolidated export completeness** — approved Russian PDF and workbook contents using one immutable brand snapshot.
6. **Product acceptance and feature freeze** — catalogue/import acceptance, optional-scope decisions, and end-to-end scenarios.

## FINAL RELEASE READINESS

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- production-like deployment checklist;
- final release workflow;
- release tag after green exact-head gates.

## LATER

- participant profiles, routes, logistics, and load distribution;
- warehouse balances, shops, prices, and price aggregation;
- broader preference modes beyond approved first-release behavior;
- organization-provided custom CSS;
- full visual reference matching from uploaded examples.

Multi-tenant support and microservices remain prohibited.
