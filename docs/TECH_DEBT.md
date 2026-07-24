# TourHub Technical Debt

Status date: 2026-07-24

## Released through TH-0093 / v0.1.0

- guided preparation, persisted shopping/equipment, recalculation, readiness, and complete Russian document package;
- production-like runtime, backup/restore, health checks, same-origin API proxy, LAN access, and restart persistence;
- typed System Settings through `h10013`;
- invitation-only Access, roles, users, and multi-session readiness through `h10016`;
- working SMTP invitation delivery with manual fallback;
- Recipe ownership/lifecycle/variants and exact assignment snapshots through `h10019`;
- append-only actor-aware AuditEvent persistence through `h10020`;
- consolidated exports and central alcohol prohibition through released head `h10021`;
- machine-readable acceptance/readiness contracts and immutable `v0.1.0` tag.

## Release-blocking debt

None. The approved first-release scope remains feature frozen and release-ready. Current post-release head is `h10023`; immutable `v0.1.0` remains at release SHA `8bcc2d2d9414d812d81634330034b15121c8442f` and released Alembic head `h10021`.

## Resolved post-release improvements

### TH-0095 through TH-0103

Project workspace navigation, Product editing, published Recipe-to-Dish synchronization, and semantic audit coverage across Project, Menu/MealSlot, System Settings/mail, invitations, catalogue/import, Shopping/Checklist, Equipment, and Documents are delivered.

### TH-0104 through TH-0107

Personal account/contact profiles, Project ownership/team access, safe filtered Audit CSV export, and own-session administration with individual revocation are delivered through current head `h10023`.

### TH-0108 through TH-0110

Product and Dish archive management preserve active contracts, history, policy lock, and transaction-owned audit. Ownership-aware Recipe CSV import adds operation-level CLUB/PERSONAL creation and actor/content/scope preview binding while preserving Product CSV and legacy CLUB compatibility. No migration was required.

### TH-0111 — Copy Project

The previously explicit Copy Project debt is resolved.

- a completed source may be copied only by its owner or an Administrator;
- ordinary editable destination parameters create a new actor-owned draft identity;
- a new schedule is built and only matching currently usable Dish/Recipe assignments are projected;
- invalid dependencies are skipped with bounded warnings;
- source owner/team, completion, history, timestamps, shopping/checklist/equipment/readiness/document state, and notifications are excluded;
- destination state and bounded `project_copied` audit share one transaction;
- duplicate-submit protection, destination result/warning presentation, unit coverage, and real-Chrome mobile acceptance are delivered;
- existing persistence was reused, so Alembic remains `h10023`.

## Remaining audit and operations debt

1. Audit retention policy and retention-management UI require approved duration, deletion eligibility, legal/operational safeguards, preview, rollback, and audit behavior.
2. External SIEM integration and operational diagnostics.
3. Scheduled/background exports and delivery.
4. Undo and event replay remain outside v0.1.0.

Automatic ORM-wide auditing remains rejected; later coverage must use semantic actions and explicit transaction ownership.

## Remaining Access and mail debt

- account recovery and verified email/phone change;
- global sign-out/revoke-all;
- Administrator access to other users' sessions;
- expired/revoked session cleanup, physical deletion, and retention policy;
- IP/device/user-agent/location tracking remains unapproved and unimplemented;
- avatars, public profiles, and account deletion;
- invitation retention and cleanup;
- asynchronous mail, retries, persisted delivery history, bounce diagnostics, templates, and attachments;
- Project-team notification provider implementations.

## Remaining Project collaboration debt

- real Project-team notifications through email, Telegram, and MAX;
- optional notification preferences and delivery history;
- richer Project search/sorting beyond completed visibility;
- participant profiles and participant-to-Project membership;
- Project retention/archive policy beyond terminal completion and explicit deletion;
- bulk team changes or reusable team templates;
- reusable named copy templates beyond one completed source operation.

## Remaining Recipe, menu, and catalogue debt

- optional moderation notifications;
- preparation technology, dietary/season metadata, and richer categories;
- Recipe-level optimistic-version decision;
- per-meal manual Recipe switching without replacing Dish;
- preference weights beyond approved generation modes;
- optional deterministic role suggestions only after separate approval;
- reviewed alcohol-policy vocabulary updates when evidence requires them;
- fuzzy/external alcohol classification and user exceptions remain out of scope.

## Remaining document and configuration debt

- scheduled/asynchronous generation and email delivery;
- persisted document versions or signatures;
- optional formats beyond approved PDF/XLSX/print/ZIP;
- versioned validated configuration archive;
- protected-value exclusion from unencrypted exports;
- approved encryption, integrity, preview, and rollback design.

## Deferred product domains

- trip-participant profiles;
- routes and GPX;
- warehouse balances, issue workflow, and participant distribution;
- procurement prices, shops, stock balances, and external aggregators.

## Product Owner decisions required for later work

- audit retention duration, deletion eligibility, safeguards, and UI;
- external SIEM/diagnostics scope;
- Project-team notification channels and preferences;
- global-sign-out, cross-user session administration, cleanup, and tracking policy;
- preference weighting and mandatory Recipe metadata;
- encrypted settings archive format.

No post-release product task is active after TH-0111. No deferred item becomes active merely because it appears here.
