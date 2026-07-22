# TourHub Technical Debt

Status date: 2026-07-22

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

### TH-0104 — Personal account

- editable FIO and optional normalized phone/Telegram/MAX/VK;
- read-only login email;
- password change preserving the current session and revoking other sessions;
- header/sidebar access to `/account` and logout inside the account;
- safe profile/password audit;
- current contact-profile migration `h10022`.

### TH-0105 — Project ownership and team access

- new Projects persist the creator as owner;
- `h10023` backfills existing ownership from trustworthy audit history with first-Administrator fallback;
- multiple additional instructors are supported, including explicitly participating Administrators;
- global User roles remain singular while owner/instructor responsibilities are Project-scoped;
- active Administrators see all Projects; owners and additional instructors see assigned Projects only;
- direct Project and nested API paths enforce one central access policy and hide unrelated Projects as 404;
- additional instructors receive read-only Menu/settings plus writable Shopping/Checklist/Equipment and document access while open;
- owners/Administrators manage team, ownership, completion, and deletion;
- ownership transfer retains the previous owner as an additional instructor in one audited transaction;
- inactive historical members lose access and regain it after reactivation;
- completed Projects are terminal read-only records hidden by default;
- Project overview owns team contacts and Project-scoped vCard; club-wide account contact listing is removed;
- a no-op notification boundary is ready for future email, Telegram, and MAX integration;
- dedicated Backend, migration, Frontend, and real-Chrome tests verify the capability matrix and mobile layout.

### TH-0106 — Audit CSV export

TH-0106 resolves the bounded audit-export portion of operational debt:

- Administrator-only filtered CSV projection beside the existing Audit list;
- one Backend filter implementation for list and export;
- deterministic UTF-8 actor/action/entity/timestamp and sanitized JSON columns;
- formula-injection neutralization;
- explicit 10,000-row bound requiring narrower filters for larger journals;
- Audit UI date filters and download action;
- Backend, Frontend, and real-Chrome acceptance;
- no persistence change, retention mutation, or recursive export AuditEvent.

## Explicit future product debt — Copy Project

`Копировать проект` is a required future Product Owner-selected task.

Expected product intent:

- source is a completed Project and remains unchanged;
- action creates a new Project identity;
- user receives the normal new-Project form for name, dates, duration, participant count, and meal boundaries;
- approved Menu and preparation/settings structure is copied from the source;
- copied data must be recalculated for the new parameters rather than reusing historical calculated quantities blindly.

Open design decisions for that future task:

- exactly which Menu manual edits, Recipes, Shopping overrides, Checklist progress, Equipment overrides, responsible-person values, comments, and generation mode are copied;
- whether the team and owner are copied or selected anew;
- audit actions and source-template attribution;
- handling of archived/prohibited catalogue dependencies;
- notifications for the newly created team;
- behavior when source snapshots are no longer valid under current policies.

No placeholder button or endpoint is implemented in TH-0106.

## Remaining Project collaboration debt

- real Project-team notifications through email, Telegram, and MAX;
- optional notification preferences and delivery history;
- richer Project search/sorting beyond completed visibility;
- participant profiles and participant-to-Project membership remain separate from instructor collaboration;
- Project retention/archive policy beyond terminal completion and explicit deletion;
- bulk team changes or reusable team templates.

## Remaining audit and operations debt after TH-0106

1. Audit retention policy and retention-management UI.
2. External SIEM integration and operational diagnostics.
3. Scheduled/background exports and delivery are not implemented.
4. Undo and event replay remain outside v0.1.0.

Automatic ORM-wide auditing remains rejected; later coverage must use semantic actions and explicit transaction ownership. Retention work must define legal/product policy before any deletion path is introduced.

## Remaining Access and mail debt

- account recovery and verified email/phone change;
- general session administration, individual revocation, cleanup, and global sign-out;
- avatars, public profiles, account deletion, and retention policy;
- invitation retention and cleanup;
- asynchronous mail, scheduled retries, persisted delivery history, and bounce diagnostics;
- approved mail templates and attachments;
- Project-team notification provider implementations.

## Remaining Recipe, menu, and catalogue debt

- optional moderation notifications;
- ownership-aware CSV import UX;
- preparation technology, dietary/season metadata, and richer categories;
- Recipe-level optimistic-version decision;
- per-meal manual Recipe switching without replacing Dish;
- preference weights beyond approved generation modes;
- Product/Dish archive-management UI;
- optional deterministic role suggestions only after separate approval;
- reviewed alcohol-policy vocabulary updates when evidence requires them;
- fuzzy/external alcohol classification and user exceptions remain out of scope.

## Remaining document debt

- scheduled/asynchronous generation;
- email delivery of generated packages;
- persisted document versions or signatures;
- optional formats beyond approved PDF/XLSX/print/ZIP.

## Deferred product domains

- trip-participant profiles;
- routes and GPX;
- warehouse balances, issue workflow, and participant distribution;
- procurement prices, shops, stock balances, and external aggregators.

## Configuration export/import debt

- versioned validated archive;
- protected-value exclusion from unencrypted exports;
- approved encryption, integrity, preview, and rollback design.

## Product Owner decisions required for later work

- audit retention duration, deletion eligibility, legal/operational safeguards, and UI;
- external SIEM/diagnostics scope;
- when to start `Копировать проект` and its exact copy matrix;
- Project-team notification channels and preferences;
- session-administration and global-sign-out policy;
- preference weighting and mandatory Recipe metadata;
- encrypted settings archive format.

No deferred item becomes active merely because it appears here. Work starts only through an explicitly selected task.
