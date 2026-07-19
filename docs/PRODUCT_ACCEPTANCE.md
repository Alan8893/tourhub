# TourHub Product Acceptance

Status: ACCEPTANCE CANDIDATE

Acceptance date: 2026-07-19

Candidate commit: assigned by PR exact-head validation

Alembic head: `h10021`

## Decision target

Accept and freeze the approved first local single-club release after one dedicated acceptance workflow and all existing repository workflows pass on the same exact head.

The acceptance source of truth is `product_acceptance_manifest.json`. This document explains the human product decision represented by that manifest.

## Accepted release capabilities

| Capability | Acceptance evidence | Decision |
|---|---|---|
| Local single-club runtime and operations | Release Compose, installation/update runbooks, backup/restore, health, clean startup, restart persistence | ACCEPT |
| Typed System Settings | Club, appearance, documents, modules, invitations, mail, users, audit responsive sections | ACCEPT |
| Access, roles, invitations, and SMTP delivery | Bootstrap, invitation-only registration, multi-session auth, role propagation, deactivation revocation, guarded routes, working mail | ACCEPT |
| Recipe ownership and publication | CLUB/PERSONAL ownership, nested authorization, submission/rejection/publication, immutable moderation audit | ACCEPT |
| Dish variants and generation modes | Ordered variants, published CLUB default, current-actor PERSONAL variants, deterministic assignment snapshots | ACCEPT |
| Project preparation | Project creation, meal boundaries, menu generation/manual edits, recalculation, shopping, checklist, equipment, readiness | ACCEPT |
| Actor-aware audit foundation | Append-only safe actor snapshots, user-access and Recipe moderation semantic history, Administrator filtering | ACCEPT |
| Consolidated Russian documents | Complete Project PDF, workbook sheets `Поход`, `Меню`, `Раскладка`, `Закупка`, `Оборудование`, compatibility ZIP | ACCEPT |
| Central alcohol prohibition | One Backend/API/import rule, HTTP 422, existing-record archival, historical preservation | ACCEPT |

## Required acceptance scenarios

### Backend API and persistence

- user administration, optimistic conflicts, multiple sessions, role propagation, and deactivation revocation;
- Recipe ownership/publication/moderation;
- Product and Recipe CSV preview/apply validation;
- project preparation status;
- actor-aware audit reads and immutability;
- complete consolidated PDF/XLSX and ZIP contract;
- central alcohol policy and reversible `h10021` data migration.

### Browser

- authentication, protected-route return, role display, logout, and revoked-session handling;
- responsive user administration;
- Recipe moderation;
- Administrator audit history;
- complete consolidated document downloads;
- guided desktop/mobile Project create → menu → prepare → reload → ZIP flow.

### Existing repository gates

- full Backend and Frontend Quality;
- Document Quality;
- Guided Release Acceptance;
- Operator Docs;
- PostgreSQL backup/restore;
- Docker Release Runtime.

## Explicitly deferred non-blocking scope

The following items are not part of the first release and do not prevent feature freeze:

- participant profiles;
- routes and GPX;
- warehouse balances, issue workflow, and participant distribution;
- procurement prices, shops, stock balances, and external aggregators;
- richer Recipe technology/tags/seasons/diet metadata and preference weights;
- per-meal manual Recipe switching without changing Dish;
- session administration, account recovery, and user profile editing;
- asynchronous mail queues, scheduled retries, bounce processing, advanced templates, and attachments;
- audit instrumentation beyond current semantic user/Recipe events;
- audit export, retention UI, SIEM, undo, and event replay;
- Product/Dish archive-management UI;
- scheduled document generation, signatures, and emailed packages;
- encrypted configuration archives;
- multi-tenancy and microservices, which remain prohibited rather than deferred.

## Feature-freeze rule

After acceptance changes to first-release scope are limited to:

1. defects found by acceptance;
2. security fixes;
3. final migration/release-readiness work;
4. documentation corrections.

Any new capability requires an explicit Product Owner decision and a post-release task.

## Pending gate

This document changes to **FEATURE FROZEN** only after the dedicated Product Acceptance workflow and all existing exact-head workflows pass. Final migration downgrade/re-upgrade and release tagging remain a separate next task.
