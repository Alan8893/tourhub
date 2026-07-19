# TourHub Technical Debt

Status date: 2026-07-19

## Released through TH-0093 / v0.1.0

- guided preparation, persisted shopping/equipment, recalculation, readiness, and complete Russian document package;
- production-like runtime, backup/restore, health checks, same-origin API proxy, LAN access, and restart persistence;
- typed System Settings through `h10013`;
- invitation-only Access, roles, users, and multi-session readiness through `h10016`;
- working SMTP invitation delivery with manual fallback;
- Recipe CLUB/PERSONAL ownership and nested authorization through `h10017`;
- Recipe lifecycle/moderation through `h10018`;
- Dish Recipe variants, three Project generation modes, and persisted assignment Recipe snapshots through `h10019`;
- append-only actor-aware AuditEvent persistence through `h10020`;
- complete consolidated Russian PDF/XLSX exports and compatibility ZIP package;
- centralized complete-word alcohol policy, archive markers, historical preservation, and `h10021`;
- machine-readable Product Acceptance and Release Readiness contracts;
- PostgreSQL 18 `h10020 → h10021 → h10020 → h10021` evidence with representative historical data;
- deployment checklist, v0.1.0 release notes, exact-head merged-main gates, and automated tag creation;
- backup-based production rollback boundary.

## Release-blocking debt

None. The approved first-release capability scope is feature frozen and release-ready. Any new blocking classification requires reproducible regression, security, migration, or operator evidence.

## Resolved post-release UX debt — TH-0095

- the Project page no longer renders Menu, Shopping, Checklist, Equipment, and Documents as one very long landing page;
- the compact Overview now exposes readiness, direct section navigation, preparation actions, and full-package download;
- Menu, Shopping, Equipment, and Documents have stable Project section URLs;
- Recipe generation mode moved into a Project settings dialog;
- Shopping calculation/packing and the purchase checklist no longer compete in a compressed two-column layout;
- checklist inputs, save actions, and purchased state remain stacked through tablet widths;
- the permanent global sidebar no longer consumes space at the Product Owner's approximately 831 px viewport and becomes a temporary drawer below desktop width;
- responsive browser acceptance covers 360 px, 831 px, and 1280 px without horizontal overflow;
- the UX improvement required no Backend, migration, calculation, authorization, or document-contract change.

## Remaining audit debt

1. Project creation/update/preparation actions.
2. Menu generation and manual MealSlot changes.
3. System Settings and mail operations with real actor attribution.
4. Invitation creation, revocation, acceptance, and delivery-result actions.
5. Catalogue/import, shopping, equipment, and document-generation actions.
6. Audit export, retention UI, external SIEM integration, and operational diagnostics.
7. Undo and event replay remain outside v0.1.0.

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

- which post-release debt slice is next after TH-0095;
- whether preference weighting beyond approved generation modes belongs in a later release;
- mandatory Recipe metadata for a later release;
- encrypted settings archive format.

No deferred item is active merely because it appears in this document. Work starts only through an explicitly selected task.
