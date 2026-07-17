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

### System Settings through merged PR #88

- PR #84: responsive `/settings`, typed club profile, approved images, `h10008`;
- PR #85: organization light/dark appearance, safe presets/import/export, `h10009`;
- PR #86: document appearance and one immutable generation snapshot, `h10010`;
- PR #87: typed module visibility, required modules, dependency locks, immediate navigation/workspace updates, `h10011`;
- PR #88: typed future invitation policy, safe default roles, normalized email domains, mandatory administrator-only rule, `h10012`;
- all persisted sections use optimistic versions, PostgreSQL row locks, HTTP 409 conflicts, and safe focused history;
- module visibility is presentation only; invitation policy is not a functional access system.

PR #84 merged as `a92cac5294ab2c7a8e1410cad7d67aaa82a2f39a`. PR #85 merged as `0e4e376470072e9475a31504faeb46e8b5a68364`. PR #86 merged as `18d5c9637e2e692b630009167dd622ee40ee2747`. PR #87 merged as `717d6f22d58e86a952edad501f05d3c67d8c0bf4`. PR #88 passed Quality #631, Document Quality #255, Guided Release Acceptance #206, Operator Docs #192, and Docker Release Runtime #187 and merged as `d79172fef861c030ff2d9e5367cf86329068b460`.

## IN PROGRESS — TH-0079 / DRAFT PR #89

### System Settings: informative mail configuration boundary

- independent singleton `MailSettings` with approved non-sensitive SMTP parameters;
- additive Alembic `h10013` with one head;
- host, port, plain/STARTTLS/TLS mode, optional username, sender identity, Reply-To, test recipient, timeout, and retry count;
- dedicated `TOURHUB_SMTP_SECRET` environment boundary with derived configured/not-configured status only;
- no secret field in PostgreSQL, request schemas, normal responses, logs, history, or UI;
- delivery and test-email actions remain unavailable until identity and access exist;
- responsive Russian editor with reset, cancel, save, conflict, version, status, and history states;
- development and release Compose pass the optional environment value to Backend without enabling delivery.

Scope boundary:

- no SMTP connection, credential verification, message generation, queue, retry execution, or delivery;
- no users, roles, sessions, authorization, functional invitations, or test-message endpoint;
- no encrypted full-system configuration archive.

## NEXT — ACCESS FOUNDATION

1. administrator bootstrap;
2. invitation-only users and functional invitation lifecycle consuming `InvitationSettings`;
3. Administrator, Instructor, and Verified Instructor roles;
4. authentication, logout, guarded routes, and backend authorization;
5. real actor identity for subsequent settings history and audit work.

## FOLLOW-UP PRODUCT WORK

1. **Working mail delivery** — consume `MailSettings` and the external SMTP secret, verify connection, send the fixed Russian test message, and connect invitations.
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
