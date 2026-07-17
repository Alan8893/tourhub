# TourHub Product Completeness Audit

Status date: 2026-07-17

## Purpose

This audit compares the approved `PRODUCT_SPEC.md` with the implemented TourHub application after merged PR #79 and the validated head of PR #80.

The audit changes release sequencing only. It does not change the approved product specification and does not implement user-facing features.

## Release decision

The final PostgreSQL migration cycle and final release workflow are deferred until the release-blocking user and domain capabilities below are implemented or explicitly removed from the first-release scope by the Product Owner.

Basic migration safety remains mandatory for every feature PR:

- exactly one Alembic head;
- upgrade of a clean PostgreSQL database to `head`;
- application startup on the migrated schema;
- backup and restore validation;
- production-like Docker startup.

The deferred final gate is the complete previous → head → previous → head migration cycle against the feature-frozen schema.

## Evidence baseline

- `main`: `99d9c2d985b8a21c62fe148e07e08b3632ef961a` — merged PR #79.
- PR #80 validated head: `73b233f7529d5d310a750071d592e9b108b9a1df`.
- Current Alembic head: `h10007`.
- Current runtime is a local single-club, single-user application.
- Current frontend routes contain placeholders for `/login` and `/dashboard`; no implemented access workflow guards the application routes.
- Current Recipe persistence contains `name` and `is_archived`, but no owner, scope, publication state, reviewer, or moderation decision.
- Current Recipe API provides create, rename, archive, restore, delete, component, note, and equipment operations without actor or role context.
- Current project documents cover purchasing and equipment outputs plus a coordinated ZIP package, not yet the complete consolidated workbook and PDF described by the approved specification.

## Completeness matrix

| Product area | Status | Evidence and gap | Release decision |
|---|---|---|---|
| Single-club local deployment | Implemented | One installation represents one club; production-like Docker runtime is covered by PR #80. | Keep. |
| Project creation and participant count | Implemented | Projects persist duration, meal boundaries, participant count, status, and preparation results. Participant changes recalculate derived purchasing and equipment data. | Keep. |
| Meal schedule | Implemented | Breakfast, snack, lunch, and dinner boundaries are persisted and browser-tested. | Keep. |
| Menu generation and manual editing | Mostly implemented | Role and meal compatibility, repeatability, calendar-day diversity, warnings, and authoritative manual slots are implemented. Instructor preference-based priority is not implemented. | Preference priority requires a Product Owner scope decision; core generation is release-ready. |
| Shopping and packaging | Implemented for the current MVP | Aggregation, package rounding, checklist state, surplus, comments, and responsible-person text are persisted. Prices, shops, and stock balances are explicitly future work. | Keep current scope. |
| Equipment | Implemented | Recipe requirements, maximum simultaneous aggregation, manual rows, overrides, removal, recalculation, and exports are implemented. | Keep. |
| Club branding | Implemented | Singleton club settings and validated PNG/JPEG logo are applied through a shared document brand snapshot. | Keep. |
| Access, invitations, and roles | Not implemented | No User/Invitation/Role persistence or API was found. `/login` and `/dashboard` are placeholders and application routes are unguarded. | Release blocker for the approved multi-user MVP unless explicitly deferred. |
| Recipe ownership and scopes | Not implemented | Recipe has no CLUB/PERSONAL scope or owner. Dish stores one selected recipe rather than multiple selectable variants. | Release blocker for the approved instructor workflow unless explicitly deferred. |
| Recipe publication and moderation | Not implemented | No submission, approval, rejection comment, reviewer, or verified-instructor workflow exists. | Release blocker if roles and shared recipe publication remain in first-release scope. |
| Recipe metadata | Partial | Components, notes, practical quantity modes, archive state, and equipment exist. Preparation technology, tags, season compatibility, dietary restrictions, and richer categories are incomplete or not represented as approved first-class fields. | Split into explicit tasks; optional metadata may be deferred only by recorded decision. |
| Consolidated PDF and Excel | Partial | Russian purchase/equipment PDF, Excel, print, and ZIP are implemented. The approved single consolidated PDF and workbook sheets `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование` are not all present as one complete release artifact. | Release blocker for specification-complete exports. Do not mix with regeneration-persistence changes. |
| Audit log | Not implemented | No actor-aware audit persistence or API was found. Existing historical fields are not the approved audit trail. | Implement after identity so actor attribution is real. |
| Alcohol prohibition | Not implemented | No centralized backend rule was found across Product API, Recipe API, CSV preview/apply, and existing-record cleanup. | Release blocker because it is an explicit invariant and cannot rely on UI validation. |
| Runtime and operator path | Implemented through PR #80 | Installation, update, backup, restore, production-like images, health checks, API proxy, clean startup, and restart persistence are covered. | Merge PR #80 independently; retain as the test platform for subsequent feature slices. |
| Final migration and release gates | Deliberately deferred | Basic Alembic, PostgreSQL, backup/restore, and Docker checks already run. Full downgrade/re-upgrade testing should target the feature-frozen schema. | Run after release-blocking feature work. |

## Recommended implementation sequence

### 1. Access foundation

- bootstrap the first administrator safely for a local installation;
- persist users, invitations, and approved roles;
- implement authentication, session handling, logout, and guarded routes;
- enforce authorization in backend services and API dependencies;
- add Russian administration UI and browser acceptance.

### 2. Recipe ownership and lifecycle

- add CLUB and PERSONAL ownership semantics;
- support multiple Recipe variants per Dish without replacing Dish identity;
- add submission, approval, rejection with comment, publication, and archive workflows;
- implement the three approved generation modes;
- preserve all existing role/meal compatibility and manual-slot rules.

### 3. Central domain safety

- implement one backend alcohol-prohibition policy used by Product, Recipe, and CSV import paths;
- reject new prohibited records consistently;
- define a reviewed migration or maintenance action for existing prohibited records;
- add API, service, import, and browser regression coverage.

### 4. Actor-aware audit log

- persist actor, action, timestamp, target, and safe metadata;
- cover project, participant, menu, recipe, publication, archive, user, and role changes;
- exclude passwords, tokens, logo bytes, and sensitive values;
- provide administrator-visible Russian history.

### 5. Export completeness

- define the final shared document data snapshot;
- produce the approved complete Russian PDF;
- produce workbook sheets `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование`;
- keep PDF, Excel, print, and ZIP mutually consistent and branded;
- keep manual-change persistence and regeneration persistence out of this slice.

### 6. Product acceptance and feature freeze

- verify active deployment catalogue classification and import interaction;
- decide whether instructor preference priority and optional recipe metadata block the first release;
- run complete role-based create → plan → prepare → export browser scenarios;
- freeze the first-release feature and schema scope.

### 7. Final release readiness

- run PostgreSQL previous → head → previous → head migration smoke on the frozen schema;
- complete the production-like deployment checklist;
- run the final release workflow;
- tag only after all exact-head gates pass.

## Scope controls

- One logical capability per PR.
- PR #80 remains a Docker runtime PR and must not absorb this audit or feature work.
- Authentication must not introduce multi-tenancy; one installation still represents one club.
- MealSlot and MealSlotDish remain primary persistence; MealPlanItem remains compatibility-only.
- Generator compatibility, ordering, repeatability, archive exclusion, and manual-slot authority remain unchanged.
- Documents remain Russian and use one immutable brand snapshot per generated package.
- No production downgrade is authorized by this audit.

## Definition of done for the audit

- every approved product-specification section has an implementation status;
- release blockers and explicit deferrals are distinguishable;
- final migration smoke is placed after feature freeze;
- the roadmap and task index point to the new implementation order;
- full repository Quality passes on the exact audit PR head.
