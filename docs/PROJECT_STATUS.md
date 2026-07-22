# TourHub Project Status

Status date: 2026-07-22

## Current phase

TourHub v0.1.0 remains release-ready at released Alembic head `h10021`. Post-release development is complete through TH-0107 at current Alembic head `h10023`. No subsequent post-release product task is selected.

The feature-frozen first release is complete through TH-0093. Post-release work delivered routed Project UX (TH-0095), Product editing (TH-0097), published Recipe-to-Dish synchronization (TH-0098), semantic audit expansion (TH-0099 through TH-0103), personal accounts/contact profiles (TH-0104), Project ownership/team-scoped access (TH-0105), safe filtered Audit CSV export (TH-0106), and own-session administration with individual revocation (TH-0107).

## Verified baseline

- PostgreSQL 18 migration cycle and one current Alembic head ending at `h10023`;
- immutable release tag `v0.1.0` at recorded release SHA `8bcc2d2d9414d812d81634330034b15121c8442f` and released migration head `h10021`;
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness on the exact TH-0107 implementation head before final task-state synchronization;
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
- one Project may have multiple additional instructors, including explicitly participating Administrators;
- global User roles remain singular; owner/additional-instructor are Project-scoped responsibilities;
- active Administrators see all Projects, while other users see only owned or assigned Projects;
- unrelated direct URLs return 404 across Project and nested boundaries;
- completed Projects are terminal read-only records and are hidden from the catalogue by default;
- ownership transfer, team changes, completion, and deletion are audited transactionally;
- Project-scoped team contacts expose approved actions without placing contact values in audit.

### Audit CSV export — TH-0106

- `/api/v1/audit/events/export.csv` remains Administrator-only through the centralized router dependency;
- list and export share Backend-owned filters for actor, entity type, entity ID, action, and created-at boundaries;
- exports contain deterministic columns for actor snapshots, semantic action, entity identity, timestamp, and already-sanitized JSON;
- UTF-8 BOM supports Russian spreadsheet review, formula-like cells are neutralized, and exports above 10,000 rows are rejected;
- export is read-only, creates no recursive AuditEvent, and introduces no migration;
- Backend, Frontend helper, and real-Chrome acceptance cover authorization, safe payloads, filtering, and mobile layout.

### Session administration — TH-0107

- `/api/v1/account/sessions` returns only the current user's active non-expired server sessions;
- response fields are limited to session ID, creation, last-seen, expiry, and current marker;
- current login matching happens server-side from the existing HttpOnly cookie hash;
- raw tokens, token hashes, cookies, IP addresses, user agents, device fingerprints, and location are excluded;
- `DELETE /api/v1/account/sessions/{id}` revokes only another owned active session;
- unrelated, revoked, expired, and unknown IDs return 404 without ownership disclosure;
- the current session returns 409 and remains available through ordinary logout;
- individual revocation and `account_session_revoked` commit or roll back together;
- safe audit context uses `current_login_preserved` and contains no session/token/cookie fields;
- `/account` exposes responsive list, current marker, revoke progress, success, and failure states;
- Backend, Frontend helper, Product Acceptance Chrome, and full real-Chrome acceptance verify immediate invalidation while preserving the current browser;
- no migration was required and current Alembic head remains `h10023`.

## Deferred non-blocking debt

- audit retention UI requires approved duration, deletion eligibility, safeguards, and rollback policy;
- global sign-out, Administrator session administration, expired/revoked-session cleanup, and any tracking metadata require separate approval;
- Project-copy implementation and future Project-team notifications through email, Telegram, and MAX;
- external SIEM integration, operational diagnostics, scheduled delivery, undo, and event replay;
- account recovery, verified contact changes, avatars, public profiles, asynchronous mail, and bounce handling;
- Product/Dish archive-management UI and ownership-aware CSV import UX;
- richer Recipe metadata, per-meal switching, preference weights, participant profiles, routes/GPX, warehouse, procurement, and external aggregation domains;
- scheduled/emailed documents, persisted versions, signatures, and encrypted configuration archives.

## Explicit future product item

`Копировать проект` remains recorded in the roadmap as a required future task. It will create a new Project from a completed Project template, reuse the ordinary new-Project parameter form, and copy approved menu/preparation settings without reopening or mutating the source. Exact copy semantics require a separate Product Owner-approved task.

## Next work

No next product task is selected. Work resumes only through a new explicit TH task, separate branch, exact-head gates, and squash merge.
