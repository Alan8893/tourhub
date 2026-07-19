# TourHub Technical Debt

Status date: 2026-07-19

## Released through TH-0093 / v0.1.0

- complete guided preparation, shopping/equipment persistence, readiness, and Russian document package;
- production-like local runtime, backup/restore, recovery, health, LAN access, and restart persistence;
- typed System Settings through `h10013`;
- invitation-only Access, roles, users, working SMTP delivery, and multi-session readiness through `h10016`;
- Recipe ownership/lifecycle/moderation through `h10018`;
- Dish variants, three Project generation modes, and assignment Recipe snapshots through `h10019`;
- append-only actor-aware AuditEvent foundation through `h10020`;
- complete consolidated Russian PDF/XLSX exports and ZIP;
- centralized alcohol policy, archive markers, historical preservation, and `h10021`;
- Product Acceptance, feature freeze, PostgreSQL final migration cycle, deployment checklist, exact-head release gates, and tag `v0.1.0`.

## Release-blocking debt

None. Tag `v0.1.0` is immutable at commit `8bcc2d2d9414d812d81634330034b15121c8442f`. New blocking classification requires reproducible regression, security, migration, or operator evidence.

## Active debt reduction — TH-0094

TH-0094 owns the first two remaining audit priorities:

1. Project creation/update/preparation actions, including participant-count changes.
2. Menu generation/regeneration and manual MealSlot Dish changes.

Implementation rules:

- semantic actions recorded by the owning business service;
- authenticated actor snapshots;
- explicit safe before/after/context values;
- business mutation and AuditEvent in one transaction;
- existing Administrator Audit API/UI reused;
- no automatic ORM-wide interceptor;
- no migration and Alembic head remains `h10021`;
- no change to released v0.1.0 behavior.

## Remaining audit debt after TH-0094

1. System Settings and mail operations with real actor attribution.
2. Invitation creation, revocation, acceptance, and delivery-result actions.
3. Catalogue/import, shopping, equipment, and document-generation actions.
4. Audit export, retention UI, external SIEM integration, and operational diagnostics.
5. Undo and event replay remain outside v0.1.0.

## Remaining Recipe, menu, and catalogue debt

- optional moderation notifications;
- ownership-aware CSV import UX beyond trusted shared-catalogue import;
- preparation technology, dietary metadata, season metadata, and richer categories;
- Recipe-level optimistic-version decision beyond serialized lifecycle transitions;
- per-meal manual Recipe switching without replacing the Dish;
- preference weights beyond the approved generation modes;
- Product/Dish archive-management UI;
- reviewed policy-vocabulary updates when real catalogue evidence requires them;
- fuzzy/external alcohol classification and user exceptions remain explicitly out of scope.

## Remaining document debt

- scheduled or asynchronous generation;
- email delivery of generated packages;
- persisted document versions or signatures;
- document-download audit events;
- optional formats beyond approved PDF/XLSX/print/ZIP.

## Remaining Access and mail debt

- account recovery and verified email change;
- session administration, individual revocation, cleanup, and global sign-out;
- user profile editing and account-retention policy;
- invitation retention and cleanup;
- asynchronous mail delivery, scheduled retries, delivery history, and bounce diagnostics;
- approved mail templates and attachments;
- additional same-origin request hardening only if deployment expands beyond trusted LAN.

## Deferred product domains

- participant profiles;
- routes and GPX;
- warehouse balances, issue workflow, and participant distribution;
- procurement prices, shops, stock balances, and external aggregators.

## Configuration export/import debt

- versioned validated archive;
- protected-value exclusion from unencrypted exports;
- approved encryption, integrity, preview, and rollback design.

## Product Owner decisions required for later releases

- which debt slice follows TH-0094;
- whether preference weighting beyond approved generation modes belongs in a later release;
- mandatory Recipe metadata for a later release;
- encrypted settings archive format.

No deferred item is active merely because it appears in this document. Work starts only through an explicitly selected task.
