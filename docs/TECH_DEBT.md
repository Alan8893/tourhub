# TourHub Technical Debt

Status date: 2026-07-19

## Implemented through TH-0091 / PR #101

- guided preparation, persisted shopping/equipment, recalculation, readiness, and Russian document package;
- production-like runtime, backup/restore, health checks, API proxy, and restart persistence;
- typed System Settings through `h10013`;
- invitation-only Access, roles, users, and multi-session readiness through `h10016`;
- working SMTP invitation delivery with manual fallback;
- Recipe CLUB/PERSONAL ownership and nested authorization through `h10017`;
- Recipe lifecycle/moderation through `h10018`;
- Dish Recipe variants, three Project generation modes, and persisted assignment Recipe snapshots through `h10019`;
- append-only actor-aware AuditEvent persistence through `h10020`;
- complete consolidated Russian PDF/XLSX exports and compatibility ZIP package;
- one centralized complete-word alcohol policy across Product, Recipe, Dish, lifecycle activation, and Product/Recipe CSV preview/apply;
- Product/Dish archive state and policy markers through `h10021`;
- deterministic archival of existing prohibited Product → Recipe → default Dish records;
- historical relationships retained while archived records are excluded from active catalogues/new preparation;
- classifier false-positive boundaries, API/import/lifecycle tests, reversible migration coverage, and complete repository acceptance.

## Remaining audit debt

1. Project creation/update/preparation actions.
2. Menu generation and manual MealSlot changes.
3. System Settings and mail operations with real actor attribution.
4. Invitation creation, revocation, acceptance, and delivery-result actions.
5. Catalogue/import, shopping, equipment, and document-generation actions.
6. Audit export, retention UI, external SIEM integration, and operational diagnostics.
7. Undo and event replay remain out of scope for the current release.

Automatic ORM-wide auditing remains rejected; later coverage must use semantic actions and the owning business transaction.

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
- additional same-origin request hardening if deployment expands beyond trusted LAN.

## Remaining release-blocking product debt

1. **Product Acceptance and Feature Freeze**.

## Configuration export/import debt

- versioned validated archive;
- protected-value exclusion from unencrypted exports;
- approved encryption, integrity, preview, and rollback design.

## Product Owner decisions still required

- whether preference weighting beyond approved generation modes belongs in a later release;
- mandatory Recipe metadata for a later release;
- encrypted settings archive format.

## Deferred final release debt

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- final deployment checklist;
- final release workflow and tag.
