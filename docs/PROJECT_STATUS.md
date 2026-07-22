# TourHub Project Status

Status date: 2026-07-22

## Current phase

TourHub v0.1.0 remains release-ready at released Alembic head `h10021`. Post-release development is complete through TH-0110 at current Alembic head `h10023`. No subsequent post-release product task is selected.

The feature-frozen first release is complete through TH-0093. Post-release work delivered routed Project UX (TH-0095), Product editing (TH-0097), published Recipe-to-Dish synchronization (TH-0098), semantic audit expansion (TH-0099 through TH-0103), personal accounts/contact profiles (TH-0104), Project ownership/team-scoped access (TH-0105), safe filtered Audit CSV export (TH-0106), own-session administration with individual revocation (TH-0107), Product archive management (TH-0108), Dish archive management (TH-0109), and ownership-aware Recipe CSV import (TH-0110).

## Verified baseline

- PostgreSQL 18 migration cycle and one current Alembic head ending at `h10023`;
- immutable release tag `v0.1.0` at recorded release SHA `8bcc2d2d9414d812d81634330034b15121c8442f` and released migration head `h10021`;
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness are required on the exact TH-0110 final head;
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only;
- the modular-monolith and single-club boundaries remain unchanged.

## Delivered post-release improvements

### Personal identity — TH-0104

Editable profile/contact fields, password change preserving the current login, Project-scoped contacts, and safe account audit are delivered through `h10022`.

### Project ownership and collaboration — TH-0105

Every Project has one owner, may have additional instructors, and is protected by centralized access masking. Team/ownership changes and terminal Project lifecycle are audited transactionally through `h10023`.

### Audit CSV export — TH-0106

Administrator-only list-aligned export uses deterministic sanitized UTF-8 JSON columns, BOM, formula neutralization, and a 10,000-row bound without a migration or recursive event.

### Session administration — TH-0107

Every active user can list only their own active non-expired sessions and revoke another owned session while current-login revocation remains ordinary logout. No tracking metadata or migration was added.

### Product archive management — TH-0108

Default Product selection remains active-only. Explicit archive management preserves history, re-runs central alcohol policy on restore, respects permanent policy lock, and commits state plus semantic audit together.

### Dish archive management — TH-0109

Default Dish selection and readiness remain active-only. Explicit archive management preserves Recipe variants, roles, and historical MealSlot/project links while enforcing policy lock and transactional audit.

### Ownership-aware Recipe CSV import — TH-0110

- Product import remains club-wide with unchanged CSV and legacy API behavior;
- Recipe import supports one explicit `club` or `personal` target per operation;
- personal imports create current-user-owned drafts and club imports create published club Recipes;
- ownership-aware preview returns a token bound to actor, content, and scope;
- apply rejects stale content/scope/token with HTTP 409 before writes or audit;
- the existing parser, duplicate/reference validation, central alcohol policy, components, notes, and all-or-nothing transaction are reused;
- legacy Recipe apply without new fields remains compatible as validated club import;
- responsive UI explains both outcomes and invalidates preview when content or scope changes;
- Backend, Frontend, Product Acceptance, and full real-Chrome coverage validate the capability;
- no migration was required and Alembic remains `h10023`.

## Deferred non-blocking debt

- audit retention UI requires approved duration, deletion eligibility, safeguards, and rollback policy;
- global sign-out, Administrator session administration, expired/revoked-session cleanup, and any tracking metadata require separate approval;
- Project-copy implementation and future Project-team notifications through email, Telegram, and MAX;
- external SIEM integration, operational diagnostics, scheduled delivery, undo, and event replay;
- account recovery, verified contact changes, avatars, public profiles, asynchronous mail, and bounce handling;
- richer Recipe metadata, per-meal switching, preference weights, participant profiles, routes/GPX, warehouse, procurement, and external aggregation domains;
- scheduled/emailed documents, persisted versions, signatures, and encrypted configuration archives.

## Explicit future product item

`Копировать проект` remains recorded in the roadmap as a required future task. It will create a new Project from a completed Project template, reuse the ordinary new-Project parameter form, and copy approved menu/preparation settings without reopening or mutating the source. Exact copy semantics require a separate Product Owner-approved task.

## Next work

No next product task is selected. Work resumes only through a new explicit TH task, separate branch, exact-head gates, and squash merge.
