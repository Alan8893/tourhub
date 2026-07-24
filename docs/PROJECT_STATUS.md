# TourHub Project Status

Status date: 2026-07-24

## Current phase

TourHub v0.1.0 remains release-ready at released Alembic head `h10021`. Post-release development is complete through TH-0111 at current Alembic head `h10023`. No subsequent post-release product task is selected.

The feature-frozen first release is complete through TH-0093. Post-release work delivered routed Project UX (TH-0095), Product editing (TH-0097), published Recipe-to-Dish synchronization (TH-0098), semantic audit expansion (TH-0099 through TH-0103), personal accounts/contact profiles (TH-0104), Project ownership/team-scoped access (TH-0105), safe filtered Audit CSV export (TH-0106), own-session administration with individual revocation (TH-0107), Product archive management (TH-0108), Dish archive management (TH-0109), ownership-aware Recipe CSV import (TH-0110), and completed-Project copying into a new draft identity (TH-0111).

## Verified baseline

- PostgreSQL 18 migration cycle and one current Alembic head ending at `h10023`;
- immutable release tag `v0.1.0` at recorded release SHA `8bcc2d2d9414d812d81634330034b15121c8442f` and released migration head `h10021`;
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness are required on the exact TH-0111 final head;
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only;
- the modular-monolith and single-club boundaries remain unchanged.

## Delivered post-release improvements

### Personal identity — TH-0104

Editable profile/contact fields, password change preserving the current login, Project-scoped contacts, and safe account audit are delivered through `h10022`.

### Project ownership and collaboration — TH-0105

Every Project has one owner, may have additional instructors, and is protected by centralized access masking. Team/ownership changes and terminal Project lifecycle are audited transactionally through `h10023`.

### Audit and session operations — TH-0106 through TH-0107

Administrator-only filtered Audit CSV export uses deterministic sanitized UTF-8 JSON columns, BOM, formula neutralization, and a 10,000-row bound. Every active user can list only their own active non-expired sessions and revoke another owned session. These capabilities added no migration.

### Catalogue lifecycle and import — TH-0108 through TH-0110

Product and Dish soft archive management preserve history and policy lock while keeping normal active projections stable. Recipe CSV import supports one explicit CLUB or PERSONAL target, actor/content/scope-bound preview/apply, current-user personal drafts, published club Recipes, legacy CLUB compatibility, and transaction-owned audit without changing Product CSV.

### Copy Project — TH-0111

- only the owner or an Administrator may copy a completed source Project;
- the destination uses editable ordinary Project parameters and receives a new ID, `draft` status, and the current actor as owner;
- the destination MealSlot schedule is recreated from its own dates/duration/meal boundaries;
- matching source assignments are copied only while Dish and selected Recipe dependencies remain currently usable;
- invalid assignments are skipped with bounded warnings;
- source Project, team, completion state, derived purchase/checklist/equipment/document state, timestamps, and history remain unchanged;
- destination persistence and `project_copied` AuditEvent share one transaction;
- Frontend navigates to the destination and presents copied/skipped counts and warnings;
- Backend, Frontend, Product Acceptance, and real-Chrome coverage validate the capability;
- no migration was required and Alembic remains `h10023`.

## Deferred non-blocking debt

- audit retention UI requires approved duration, deletion eligibility, safeguards, and rollback policy;
- global sign-out, Administrator session administration, expired/revoked-session cleanup, and any tracking metadata require separate approval;
- Project-team notifications through email, Telegram, and MAX, reusable team templates, and richer Project search;
- external SIEM integration, operational diagnostics, scheduled delivery, undo, and event replay;
- account recovery, verified contact changes, avatars, public profiles, asynchronous mail, and bounce handling;
- richer Recipe metadata, per-meal switching, preference weights, participant profiles, routes/GPX, warehouse, procurement, and external aggregation domains;
- scheduled/emailed documents, persisted versions, signatures, and encrypted configuration archives.

## Next work

No next product task is selected. Work resumes only through a new explicit TH task, separate branch, exact-head gates, and squash merge.
