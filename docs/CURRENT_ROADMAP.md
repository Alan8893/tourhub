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
      → Guarded preparation routes and backend authorization
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
- System Settings scheduled before Access foundation.

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

### Access foundation through PR #92

- PR #90: typed users and sessions, one-time Administrator bootstrap, protected System Settings, and `h10014`;
- PR #91: typed invitation lifecycle, public acceptance, initial sign-in, manual delivery, and `h10015`;
- PR #92: user list, explicit roles, activation state, conflict protection, final-active-Administrator invariant, and `h10016`;
- raw session and invitation values are not retained in PostgreSQL;
- automatic mail delivery remains separate.

PR #90 merged as `26c4d4eb9246de44579451fe3d6e7bd631538324`. PR #91 merged as `2348870864efa1da20547c1a6564dc5f9b6488ef`. PR #92 merged as `257d82a9f4f7e47095f8e96635bf62a9ed14e722`.

## IN PROGRESS — TH-0083 / DRAFT PR #93

### Access: preparation authorization matrix

- one Backend dependency protects project, catalogue, import, menu, shopping, equipment, document, dish, and current recipe endpoints;
- active Administrator, Instructor, and Verified Instructor roles receive preparation access;
- health, bootstrap/login, and invitation inspection/acceptance remain public;
- System Settings, invitation administration, and user administration remain Administrator-only;
- one frontend guard protects the full `AppLayout` route tree and preserves the requested destination through login;
- release-runtime smoke now performs bootstrap/login before project persistence checks;
- no migration is required; the database head remains `h10016`.

Scope boundary:

- recipe publication and moderation distinctions remain part of recipe ownership/lifecycle;
- no per-project ownership or row-level access;
- no actor-aware audit or account-recovery work in this PR.

## NEXT

1. **Working mail delivery** — consume `MailSettings` and the external deployment value, verify the connection, send the fixed Russian test message, and connect automatic invitation delivery.
2. **Recipe ownership and lifecycle** — CLUB/PERSONAL ownership, variants, publication, moderation, and generation modes.
3. **Central alcohol prohibition** — one backend policy across Product, Recipe, and CSV import paths.
4. **Actor-aware audit log** — safe history for project, menu, recipe, user, role, mail, and settings changes.
5. **Consolidated export completeness** — approved complete Russian PDF and workbook contents using one immutable brand snapshot.
6. **Product acceptance and feature freeze** — catalogue/import acceptance, optional-scope decisions, and end-to-end scenarios.

## Deferred Access operations

- session administration, cleanup, global sign-out, and account-recovery policy;
- additional same-origin request hardening if deployment expands beyond trusted LAN;
- external identity providers and MFA.

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
