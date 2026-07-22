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

Editable profile/contact fields, read-only login email, password change preserving the current login, Project-scoped contacts, safe account audit, and migration `h10022` are delivered.

### TH-0105 — Project ownership and team access

Project ownership/team persistence through `h10023`, central access masking, terminal completion, transactional team/ownership audit, Project-scoped contacts, and the future notification boundary are delivered.

### TH-0106 — Audit CSV export

Administrator-only filtered deterministic CSV export with shared Backend filters, UTF-8 BOM, formula neutralization, 10,000-row bound, date-filter UX, and Backend/Frontend/Chrome coverage is delivered without a migration or recursive event.

### TH-0107 — Session administration

Own active-session projection, server-side current-login matching, individual revocation, 404 ownership masking, 409 current-login protection, transactional safe audit, responsive `/account` UX, and real-Chrome coverage are delivered without tracking metadata, cleanup, or migration.

### TH-0108 — Product archive management

- active Product selection remains the stable default contract;
- a protected archive projection exposes Product archive and policy-lock state;
- preparation users can soft-archive and restore one Product;
- archive preserves all historical Recipe, shopping, checklist, and document references;
- restore re-runs the central alcohol policy;
- policy-archived Products are permanently non-restorable through this capability;
- archive/restore use row locks, idempotency, and transactional `product_archived` / `product_restored` events;
- existing Recipe/Product response contracts remain stable through dedicated archive DTOs;
- responsive active/archive UI, policy-lock explanation, tests, and real-Chrome acceptance are delivered;
- existing Product archive columns were reused, so Alembic remains `h10023`.

### TH-0109 — Dish archive management

- active Dish selection and catalogue readiness remain the stable default contract;
- a protected archive projection exposes Dish archive and policy-lock state;
- preparation users can soft-archive and restore one Dish;
- archive preserves Recipe variants, meal roles, and historical MealSlot/project references;
- restore re-runs the central Dish-name alcohol policy;
- policy-archived Dishes are permanently non-restorable through this capability;
- archive/restore use row locks, idempotency, and transactional `dish_archived` / `dish_restored` events;
- existing Dish/Recipe response contracts remain stable through dedicated archive DTOs;
- responsive active/archive UI, policy-lock explanation, tests, and real-Chrome acceptance are delivered;
- existing Dish archive columns were reused, so Alembic remains `h10023`.

## Explicit future product debt — Copy Project

`Копировать проект` is a required future Product Owner-selected task.

Expected product intent:

- source is a completed Project and remains unchanged;
- action creates a new Project identity;
- user receives the normal new-Project form for name, dates, duration, participant count, and meal boundaries;
- approved Menu and preparation/settings structure is copied from the source;
- copied data is recalculated for new parameters instead of blindly reusing historical quantities.

Open decisions include the exact copy matrix, team/owner handling, audit attribution, archived/prohibited dependencies, notifications, and policy-invalid historical snapshots. No placeholder button or endpoint is implemented.

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
- bulk team changes or reusable team templates.

## Remaining Recipe, menu, and catalogue debt

- ownership-aware CSV import UX;
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
- when to start `Копировать проект` and its exact copy matrix;
- Project-team notification channels and preferences;
- global-sign-out, cross-user session administration, cleanup, and tracking policy;
- ownership-aware import semantics;
- preference weighting and mandatory Recipe metadata;
- encrypted settings archive format.

No post-release product task is active after TH-0109. No deferred item becomes active merely because it appears here.
