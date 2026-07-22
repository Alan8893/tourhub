# TourHub Project Status

Status date: 2026-07-22

## Current phase

TourHub v0.1.0 remains release-ready at released Alembic head `h10021`. Post-release development is complete through TH-0108 at current Alembic head `h10023`. No subsequent post-release product task is selected.

The feature-frozen first release is complete through TH-0093. Post-release work delivered routed Project UX (TH-0095), Product editing (TH-0097), published Recipe-to-Dish synchronization (TH-0098), semantic audit expansion (TH-0099 through TH-0103), personal accounts/contact profiles (TH-0104), Project ownership/team-scoped access (TH-0105), safe filtered Audit CSV export (TH-0106), own-session administration with individual revocation (TH-0107), and Product archive management (TH-0108).

## Verified baseline

- PostgreSQL 18 migration cycle and one current Alembic head ending at `h10023`;
- immutable release tag `v0.1.0` at recorded release SHA `8bcc2d2d9414d812d81634330034b15121c8442f` and released migration head `h10021`;
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness on the exact TH-0108 implementation head before final task-state synchronization;
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only;
- the modular-monolith and single-club boundaries remain unchanged.

## Delivered post-release improvements

### Personal identity — TH-0104

- `/account` contains FIO, read-only email, optional phone/Telegram/MAX/VK, password change, and logout;
- profile contact values are normalized by Backend and exposed only through a visible Project team;
- password change preserves the current login and revokes other sessions;
- account audit excludes contact values, passwords, hashes, cookies, and tokens.

### Project ownership and collaboration — TH-0105

- every new Project stores its creator as owner;
- `h10023` backfills existing owners from trustworthy `project_created` audit history with first-Administrator fallback;
- one Project may have multiple additional instructors while global User roles remain singular;
- central Project access masks unrelated resources as 404 and completed Projects remain terminal read-only history;
- team/ownership changes and Project status/deletion are audited transactionally.

### Audit CSV export — TH-0106

- `/api/v1/audit/events/export.csv` remains Administrator-only;
- list and export share Backend-owned actor, entity, action, and date filters;
- exports contain deterministic sanitized UTF-8 JSON columns, BOM, formula neutralization, and a 10,000-row bound;
- export is read-only, creates no recursive AuditEvent, and introduces no migration.

### Session administration — TH-0107

- `/api/v1/account/sessions` returns only the current user's active non-expired server sessions;
- raw tokens, token hashes, cookies, IP addresses, user agents, device fingerprints, and location are excluded;
- `DELETE /api/v1/account/sessions/{id}` revokes only another owned active session;
- current-session revocation is blocked and individual revocation is audited transactionally;
- responsive `/account` UX and real-Chrome acceptance verify immediate invalidation while preserving the current browser.

### Product archive management — TH-0108

- default `/api/v1/products` remains active-only and retains its stable response shape;
- `/api/v1/products/archive` explicitly projects archived Product records and alcohol-policy lock state;
- archive and restore require preparation access, lock the Product row, and commit state plus semantic audit together;
- archive is soft and never deletes Product or historical Recipe, purchase, checklist, or document references;
- manually archived Products can be restored only after the central alcohol policy passes again;
- `archived_by_alcohol_policy` Products remain archived and non-restorable;
- repeat archive/restore calls are idempotent and create no duplicate audit event;
- the Product catalogue provides responsive active/archive management with policy-lock explanation;
- Backend, Frontend, Product Acceptance, and full real-Chrome coverage are green;
- no migration was required and Alembic remains `h10023`.

## Deferred non-blocking debt

- audit retention UI requires approved duration, deletion eligibility, safeguards, and rollback policy;
- global sign-out, Administrator session administration, expired/revoked-session cleanup, and any tracking metadata require separate approval;
- Project-copy implementation and future Project-team notifications through email, Telegram, and MAX;
- external SIEM integration, operational diagnostics, scheduled delivery, undo, and event replay;
- account recovery, verified contact changes, avatars, public profiles, asynchronous mail, and bounce handling;
- Dish archive-management UI and ownership-aware CSV import UX;
- richer Recipe metadata, per-meal switching, preference weights, participant profiles, routes/GPX, warehouse, procurement, and external aggregation domains;
- scheduled/emailed documents, persisted versions, signatures, and encrypted configuration archives.

## Explicit future product item

`Копировать проект` remains recorded in the roadmap as a required future task. It will create a new Project from a completed Project template, reuse the ordinary new-Project parameter form, and copy approved menu/preparation settings without reopening or mutating the source. Exact copy semantics require a separate Product Owner-approved task.

## Next work

No next product task is selected. Work resumes only through a new explicit TH task, separate branch, exact-head gates, and squash merge.
