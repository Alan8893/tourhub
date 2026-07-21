# TourHub Technical Debt

Status date: 2026-07-21

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
- centralized complete-word alcohol policy, archive markers, historical preservation, and released head `h10021`;
- machine-readable Product Acceptance and Release Readiness contracts;
- PostgreSQL 18 migration-cycle evidence, deployment checklist, exact-head gates, and immutable `v0.1.0` tag;
- backup-based production rollback boundary.

## Release-blocking debt

None. The approved first-release capability scope is feature frozen and release-ready. Any new blocking classification requires reproducible regression, security, migration, or operator evidence.

## Resolved post-release improvements

### TH-0095 through TH-0098 — Workspace and catalogue workflow

Project workspace routing, shared Product editing, and transactional published Recipe-to-Dish synchronization are delivered without changing the single-club or modular-monolith boundaries.

### TH-0099 through TH-0103 — Semantic audit coverage

Project, Menu/MealSlot, System Settings/mail, invitations, catalogue/import, shopping, equipment, and document-generation writes record bounded actor-attributed events at explicit transaction/result boundaries. No-op writes are suppressed, audit failure rolls back pending transactional mutations, and protected values are excluded.

### TH-0104 — Personal account and club contacts

- `/account` is available to every authenticated active user;
- the global header opens the personal account instead of exposing a logout action;
- the sidebar includes `Личный кабинет`;
- existing `display_name` serves as one FIO field and email remains read-only;
- `h10022` adds nullable phone, Telegram, MAX, and VK fields;
- Backend normalizes human-friendly phone input and handle/full-link social input;
- social links are restricted to approved Telegram, MAX, and VK HTTPS hosts;
- active users may view active club contacts only after authentication;
- `mailto:`, `tel:`, social links, and generated vCard support mobile contact use;
- password change verifies the current password, preserves the current login, and revokes every other active login;
- profile update and password change share their AuditEvent transaction and roll back together on audit failure;
- profile no-op saves create no event;
- account audit stores versions, changed field names, current-login preservation, and revoked-login count only;
- phone numbers, social URLs, passwords, hashes, cookies, raw session values, and tokens are excluded from audit payloads;
- strict Ruff/mypy, full Backend regression, migration tests, Product Acceptance, full browser acceptance, backup/restore, Alembic, Docker, documentation, guided-release, operator, and final-readiness gates verify the implementation;
- current post-release Alembic head is `h10022`; immutable `v0.1.0` remains at released head `h10021`.

## Remaining audit debt

1. Audit export, retention UI, external SIEM integration, and operational diagnostics.
2. Undo and event replay remain outside v0.1.0.

Automatic ORM-wide auditing remains rejected; later coverage must use semantic actions and explicit transaction ownership.

## Remaining Recipe, menu, and catalogue debt

- optional moderation notifications;
- ownership-aware CSV import UX beyond trusted shared-catalogue import;
- preparation technology, dietary metadata, season metadata, and richer categories;
- Recipe-level optimistic-version decision beyond serialized lifecycle transitions;
- per-meal manual Recipe switching without replacing the Dish;
- preference weights beyond the approved generation modes;
- Product/Dish archive-management UI;
- optional role suggestions only after a separately approved deterministic policy; automatic inference remains rejected;
- reviewed policy-vocabulary updates when real catalogue evidence requires them;
- fuzzy/external alcohol classification and user exceptions remain explicitly out of scope.

## Remaining document debt

- scheduled or asynchronous generation;
- email delivery of generated packages;
- persisted document versions or signatures;
- optional formats beyond approved PDF/XLSX/print/ZIP.

## Remaining Access, profile, and mail debt

- account recovery and verified email change;
- email and phone verification;
- avatar upload and public member profile presentation;
- account deletion and retention policy;
- general session administration, individual login revocation, cleanup, and global sign-out UI;
- invitation retention and cleanup;
- asynchronous mail delivery, scheduled retries, persisted delivery history, and bounce diagnostics;
- approved mail templates and attachments;
- additional same-origin request hardening only if deployment expands beyond trusted LAN.

## Deferred product domains

- trip-participant profiles distinct from User contact profiles;
- routes and GPX;
- warehouse balances, issue workflow, and participant distribution;
- procurement prices, shops, stock balances, and external aggregators.

## Configuration export/import debt

- versioned validated archive;
- protected-value exclusion from unencrypted exports;
- approved encryption, integrity, preview, and rollback design.

## Product Owner decisions required for later releases

- which post-release debt slice follows TH-0104;
- whether audit export/retention/diagnostics belongs in the next release;
- whether verified contact changes or session administration should follow;
- whether preference weighting beyond approved generation modes belongs in a later release;
- mandatory Recipe metadata for a later release;
- encrypted settings archive format.

No deferred item is active merely because it appears in this document. Work starts only through an explicitly selected task.
