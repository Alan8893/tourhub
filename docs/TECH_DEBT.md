# TourHub Technical Debt

Status date: 2026-07-19

## Implemented through TH-0090 / PR #100

- guided preparation, persisted shopping/equipment, recalculation, readiness, and Russian document package;
- production-like runtime, backup/restore, health checks, API proxy, and restart persistence;
- typed System Settings through `h10013`;
- invitation-only Access, roles, users, and multi-session readiness through `h10016`;
- working SMTP invitation delivery with manual fallback;
- Recipe CLUB/PERSONAL ownership and nested authorization through `h10017`;
- Recipe lifecycle and moderation through `h10018`;
- ordered Dish Recipe variants, three Project generation modes, and persisted assignment Recipe snapshots through `h10019`;
- assignment-based shopping/equipment calculations;
- append-only actor-aware AuditEvent persistence through `h10020`;
- semantic user role/activation and Recipe submit/publish/reject history in the same business transaction;
- immutable Recipe moderation history beyond the latest Recipe fields;
- bounded recursive secret-field removal, Administrator query API, responsive Audit UI, and focused Backend/Chrome acceptance;
- complete consolidated Russian PDF and workbook exports with persisted assignment Recipe names;
- approved workbook sheets `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование`;
- one immutable branding snapshot per document package request;
- compatibility purchase/equipment documents preserved alongside complete artifacts in ZIP;
- focused document Backend, API, package, and desktop/mobile Chrome acceptance.

## Remaining audit debt

1. Project creation/update/preparation actions.
2. Menu generation and manual MealSlot changes.
3. System Settings and mail operations with real actor attribution.
4. Invitation creation, revocation, acceptance, and delivery-result actions.
5. Catalogue, CSV import, Product, Dish, and Recipe component/note/equipment edits beyond lifecycle transitions.
6. Shopping, equipment, and document-generation actions.
7. Audit export, retention policy/UI, external SIEM integration, and operational diagnostics.
8. Undo and event replay remain explicitly out of scope for the current release.

Automatic ORM-wide auditing remains rejected; later coverage must use semantic actions and the owning business transaction.

## Remaining Recipe and menu debt

- optional moderation notifications;
- ownership-aware CSV import UX beyond trusted shared-catalogue import;
- preparation technology, dietary metadata, season metadata, and richer categories;
- decide whether Recipe-level optimistic versions are required beyond serialized lifecycle transitions;
- per-meal manual Recipe switching without replacing the Dish;
- preference weights or ranking beyond `club_only`, `club_and_personal`, and `personal_preferred`.

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
- additional same-origin request hardening if deployment expands beyond trusted LAN.

## Remaining release-blocking product debt

1. **Central alcohol prohibition** across Product, Recipe, Dish, and CSV import, including existing-record handling.
2. **Product acceptance and feature freeze**.

## Configuration export/import debt

- versioned validated archive;
- protected-value exclusion from unencrypted exports;
- approved encryption, integrity, preview, and rollback design.

## Product Owner decisions still required

- whether preference weighting beyond the approved generation modes belongs in a later release;
- mandatory Recipe metadata for first release;
- encrypted settings archive format.

## Deferred final release debt

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- final deployment checklist;
- final release workflow and tag.
