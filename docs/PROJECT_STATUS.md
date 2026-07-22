# TourHub Project Status

Status date: 2026-07-22

## Current phase

TourHub v0.1.0 remains release-ready at released Alembic head `h10021`. Post-release development is complete through TH-0105 at current head `h10023`. TH-0106 is the single active implementation candidate.

The feature-frozen first release is complete through TH-0093. Post-release work delivered routed Project UX (TH-0095), Product editing (TH-0097), published Recipe-to-Dish synchronization (TH-0098), semantic audit expansion (TH-0099 through TH-0103), personal accounts/contact profiles (TH-0104), and Project ownership/team-scoped access (TH-0105).

## Verified baseline

- PostgreSQL 18 migration cycle and one current Alembic head ending at `h10023`;
- immutable release tag `v0.1.0` at recorded release SHA `8bcc2d2d9414d812d81634330034b15121c8442f` and released migration head `h10021`;
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness on the exact TH-0105 head;
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only;
- the modular-monolith and single-club boundaries remain unchanged.

## Delivered post-release improvements

### Personal identity

- `/account` contains FIO, read-only email, optional phone/Telegram/MAX/VK, password change, and logout;
- profile contact values are normalized by Backend;
- contact values are no longer exposed through a club-wide account directory;
- password change preserves the current login and revokes other sessions;
- account audit excludes contact values, passwords, hashes, cookies, and tokens.

### Project ownership and collaboration — TH-0105

- every new Project stores its creator as owner;
- `h10023` backfills existing owners from trustworthy `project_created` audit history with first-Administrator fallback;
- one Project may have multiple additional instructors, including explicitly participating Administrators;
- global User roles remain singular; owner/additional-instructor are Project-scoped responsibilities;
- active Administrators see all Projects, while other users see only owned or assigned Projects;
- unrelated direct URLs return 404 across Project, Menu, preparation, shopping/checklist, equipment, documents, team contacts, settings, status, and deletion boundaries;
- additional instructors may view Menu and operate Shopping, Checklist, Equipment, Documents, and Project contacts, but cannot write Menu or Project/team settings;
- owners and Administrators may manage team membership, transfer ownership, complete, and delete Projects;
- ownership transfer keeps the previous owner as an additional instructor in one audited transaction;
- inactive owners/team members remain historical members but lose runtime access until reactivation;
- completed Projects are terminal read-only records and are hidden from the Project catalogue by default;
- the Project overview contains team contact cards with mail, phone, Telegram, MAX, VK, and Project-scoped vCard actions;
- a no-op notification boundary is ready for later email, Telegram, and MAX integration without sending messages now;
- Russian Audit UI labels cover instructor add/remove, ownership transfer, status change, and deletion.

## Active TH-0106 candidate — Audit CSV export

- `/api/v1/audit/events/export.csv` remains Administrator-only through the existing centralized router dependency;
- list and export share Backend-owned filters for actor, entity type, entity ID, action, and created-at boundaries;
- exports contain deterministic columns for actor snapshots, semantic action, entity identity, timestamp, and already-sanitized before/after/context JSON;
- UTF-8 BOM supports Russian spreadsheet review, while formula-like cells are neutralized;
- exports above 10,000 matching rows are rejected with a clear bounded error;
- the Audit UI adds date filters and a filtered `Скачать CSV` action;
- export is read-only, creates no recursive AuditEvent, and introduces no migration;
- Backend, Frontend helper, and dedicated real-Chrome acceptance are included in the candidate.

## TH-0106 non-goals

Retention deletion/cleanup, retention-policy UI, external SIEM delivery, operational diagnostics, scheduled exports, background processing, undo, replay, session administration, Product/Dish archive-management UI, ownership-aware import UX, and Project copy remain separate work.

## Explicit future product item

`Копировать проект` remains recorded in the roadmap as a required future task. It will create a new Project from a completed Project template, reuse the ordinary new-Project parameter form, and copy approved menu/preparation settings without reopening or mutating the source. Exact copy semantics require a separate Product Owner-approved task.

## Deferred non-blocking debt

- Project-copy implementation and future Project-team notifications through email, Telegram, and MAX;
- audit retention UI, external SIEM integration, operational diagnostics, undo, and event replay;
- account recovery, verified contact changes, session administration, avatars, public profiles, asynchronous mail, and bounce handling;
- richer Recipe metadata, per-meal switching, preference weights, and ownership-aware import UX;
- Product/Dish archive-management UI;
- participant profiles, routes/GPX, warehouse, procurement, and external aggregation domains;
- scheduled/emailed documents, persisted versions, signatures, and encrypted configuration archives.

## Next work

TH-0106 is the only active task. It is complete only after all exact-head gates pass, review threads are clear, the branch matches current `main`, task state moves to `closed`, and the PR is squash-merged.
