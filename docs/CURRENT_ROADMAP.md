# TourHub Current Roadmap

Status date: 2026-07-17

## Product goal

Deliver the approved local MVP for one tourist club without changing the approved architecture.

```text
Project preparation baseline
  → Production-like Docker runtime
  → Product completeness audit
  → System Settings foundation
      → Club profile and settings shell
      → Site appearance
      → Document appearance
      → Module visibility and dependency locks
      → Future invitation policy
      → Informative mail configuration boundary
  → Access and roles
  → Working mail delivery
  → Recipe ownership and lifecycle
  → Central domain safety
  → Actor-aware audit
  → Consolidated Russian exports
  → Product acceptance and feature freeze
  → Final migration and release gates
```

## DONE

### Infrastructure and guided preparation

- Docker Compose, PostgreSQL 18, Redis, and one-head Alembic validation;
- backend Ruff, strict mypy, pytest, frontend tests/build/browser acceptance;
- PostgreSQL backup/restore CI;
- project creation, role-aware menu generation, authoritative editing, shopping, equipment, recalculation, and readiness;
- Russian purchase/equipment PDF, Excel, print, and ZIP;
- desktop/mobile guided preparation acceptance.

PR #77 merged as `18d4fabde3eda6c83c0c0f998e870a6f043e8dec`. PR #78 merged as `6332ef5f86973c7832e92dc1ef0a681cc4e17d1e`.

### Operations and release runtime

- installation, update, health, migration, LAN, backup, restore, and recovery runbooks;
- standalone release Compose and production Nginx frontend;
- internal PostgreSQL/Redis networking, same-origin API proxy, clean startup, migration-head, and restart-persistence checks.

PR #79 merged as `99d9c2d985b8a21c62fe148e07e08b3632ef961a`. PR #80 merged as `939828e8c335966dde2d04c5083ee7d2da07c6eb`.

### Product completeness audit

- approved product scope compared with actual implementation;
- mandatory user/domain gaps separated from later work;
- final downgrade/re-upgrade cycle moved after feature freeze;
- System Settings scheduled before access foundation.

PR #83 merged as `950a43914230f6fe4be3bf217a4e5f1b79e7265f`.

### System Settings through merged PR #87

- PR #84: responsive `/settings`, typed club profile, approved images, `h10008`;
- PR #85: organization light/dark appearance, safe presets/import/export, `h10009`;
- PR #86: independent document appearance and one immutable generation snapshot, `h10010`;
- PR #87: typed module visibility, required modules, document dependency locks, immediate navigation/workspace updates, `h10011`;
- all sections use optimistic versions, PostgreSQL row locks, HTTP 409 conflicts, and safe focused history;
- direct routes and APIs remain available when modules are hidden; visibility is not authorization.

PR #84 merged as `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a`. PR #85 merged as `0e4e376470072e9475a31504faeb46e8b5a68364`. PR #86 merged as `18d5c9637e2e692b630009167dd622ee40ee2747`. PR #87 passed Quality #604, Document Quality #229, Guided Release Acceptance #180, Operator Docs #166, and Docker Release Runtime #161 and merged as `717d6f22d58e86a952edad501f05d3c67d8c0bf4`.

## IN PROGRESS — TH-0078 / DRAFT PR #88

### System Settings: future invitation policy

- independent singleton `InvitationSettings` and additive Alembic `h10012`;
- invitation lifetime from 1 to 90 days;
- safe default role limited to Instructor or Verified Instructor;
- optional allowed email-domain list, normalized to lowercase IDNA and deduplicated by the backend;
- resend permission, active-invitation limit, and email-confirmation requirement;
- mandatory administrator-only management protected by API validation and a database check;
- versioned row-locked updates, HTTP 409 conflicts, and safe `invitations` history;
- responsive Russian editor with reset, cancel, save, conflict, version, and history states;
- explicit UI notice that users, tokens, emails, and the invitation list are not operational yet.

Scope boundary:

- no User or Invitation persistence;
- no token generation, acceptance, revocation, or resend execution;
- no registration, login, sessions, role authorization, SMTP, or email delivery;
- saved policy becomes an input to the later Access foundation.

## NEXT — FINAL SYSTEM SETTINGS BOUNDARY

1. **Informative mail configuration boundary**
   - describe universal SMTP ownership and the external/write-only password boundary;
   - store only approved non-secret future mail parameters if required by the slice;
   - no working delivery or test email until identity exists.

## FOLLOW-UP PRODUCT WORK

1. **Access foundation** — administrator bootstrap, invitation-only users, roles, authentication, guarded routes, backend authorization, and functional invitation lifecycle.
2. **Working mail delivery** — universal SMTP, external/write-only password, sender identity, test address, retries, status, and fixed Russian test message.
3. **Recipe ownership and lifecycle** — CLUB/PERSONAL ownership, variants, publication, moderation, and generation modes.
4. **Central alcohol prohibition** — one backend policy across Product, Recipe, and CSV import paths.
5. **Actor-aware audit log** — safe history for project, menu, recipe, user, role, mail, and settings changes.
6. **Consolidated export completeness** — approved Russian PDF and workbook contents using one immutable brand snapshot.
7. **Product acceptance and feature freeze** — catalogue/import acceptance, optional-scope decisions, and end-to-end scenarios.

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
