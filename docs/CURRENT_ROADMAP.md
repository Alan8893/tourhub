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
      → Functional invitations and user administration
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
- PR #88: future invitation policy, safe default roles and normalized domains, `h10012`;
- PR #89: non-secret mail metadata and external SMTP-secret status boundary, `h10013`;
- all persisted settings sections use typed ownership, optimistic versions, PostgreSQL row locks, HTTP 409 conflicts, and safe focused history;
- visibility is not authorization, invitation policy is not an invitation subsystem, and mail metadata does not send email.

PR #84 merged as `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a`. PR #85 merged as `0e4e376470072e9475a31504faeb46e8b5a68364`. PR #86 merged as `18d5c9637e2e692b630009167dd622ee40ee2747`. PR #87 merged as `717d6f22d58e86a952edad501f05d3c67d8c0bf4`. PR #88 merged as `d79172fef861c030ff2d9e5367cf86329068b460`. PR #89 passed Quality #660, Document Quality #283, Guided Release Acceptance #234, Operator Docs #220, and Docker Release Runtime #215 and merged as `bff7950e3542b719983f2a09b61b9a901fbaca64`.

## IN PROGRESS — TH-0080 / DRAFT PR #90

### Access: first Administrator and server sessions

- typed `User`, `IdentityState`, and `AuthSession` persistence;
- additive Alembic `h10014` with one head;
- one-time transactional bootstrap of the first Administrator;
- memory-hard password hashing with no plaintext credential persistence;
- opaque random session cookie with HttpOnly and SameSite=Lax;
- only a SHA-256 session-token hash is stored server-side;
- public bootstrap status, bootstrap, login, logout, and current-user endpoints;
- server-side expiry and revocation;
- Administrator authorization for all System Settings APIs;
- guarded `/settings`, responsive bootstrap/login page, user identity, and logout action;
- preparation routes and APIs remain available in this first access slice.

Scope boundary:

- no functional invitations, user list, role editing, deactivation, or password reset;
- no protection of every project/catalogue/preparation route or endpoint yet;
- no external identity provider, MFA, refresh-token family, or multi-tenancy.

## NEXT — ACCESS FOUNDATION CONTINUATION

1. functional invitation lifecycle consuming `InvitationSettings`;
2. user list, activation state, and explicit role management;
3. broader guarded frontend routes and backend authorization for preparation mutations;
4. actor-aware identity propagation into settings history and the later audit log.

## FOLLOW-UP PRODUCT WORK

1. **Working mail delivery** — consume `MailSettings` and the external SMTP value, verify connection, send the fixed Russian test message, and connect invitations.
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
