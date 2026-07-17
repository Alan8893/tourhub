# TourHub Product Completeness Audit

Status date: 2026-07-17

## Purpose

This audit compares the approved `PRODUCT_SPEC.md` with the implemented TourHub application after merged PR #80.

The audit changes release sequencing only. It does not change the approved product specification and does not implement user-facing features.

## Release decision

The final PostgreSQL migration cycle and final release workflow are deferred until the first-release user and domain scope is implemented or explicitly deferred by the Product Owner.

Basic migration safety remains mandatory for every feature PR:

- exactly one Alembic head;
- upgrade of a clean PostgreSQL database to `head`;
- application startup on the migrated schema;
- PostgreSQL backup and restore validation;
- production-like Docker startup.

The complete previous → head → previous → head migration cycle remains a final feature-freeze gate.

## Evidence baseline

- `main`: `939828e8c335966dde2d04c5083ee7d2da07c6eb` — merged PR #80.
- Current Alembic head: `h10007`.
- Production-like Docker image build, clean startup, API proxying, health checks, migration head, and restart persistence are validated.
- Current runtime is a local single-club, single-user application.
- Singleton club name and logo settings exist and feed one document brand snapshot.
- There is no complete unified system-settings surface for appearance, module configuration, mail, or invitation policy.
- Current frontend access routes are placeholders; application routes are not protected by an implemented identity workflow.
- Recipe persistence has no owner, CLUB/PERSONAL scope, publication state, reviewer, or moderation decision.
- Current project documents cover purchasing and equipment outputs plus a coordinated ZIP, not the complete consolidated workbook and PDF from the approved specification.

## Completeness matrix

| Product area | Status | Evidence and gap | Release decision |
|---|---|---|---|
| Single-club local deployment | Implemented | One installation represents one club; production-like Docker runtime was merged in PR #80. | Keep. |
| Project creation and participant count | Implemented | Projects persist duration, meal boundaries, participant count, status, and preparation results. Participant changes recalculate derived data. | Keep. |
| Meal schedule | Implemented | Breakfast, snack, lunch, and dinner boundaries are persisted and browser-tested. | Keep. |
| Menu generation and manual editing | Mostly implemented | Role/meal compatibility, repeatability, calendar-day diversity, warnings, and authoritative manual slots are implemented. Preference-based priority is missing. | Product Owner decision required for preference priority. |
| Shopping and packaging | Implemented for current MVP | Aggregation, rounding, checklist state, surplus, comments, and responsible-person text are persisted. | Keep current scope. |
| Equipment | Implemented | Requirements, maximum simultaneous aggregation, manual rows, overrides, removals, recalculation, and exports are implemented. | Keep. |
| Club branding | Implemented | Singleton name and validated PNG/JPEG logo use a shared document brand snapshot. | Preserve while extending settings. |
| Unified system settings | Partial | Branding exists, but there is no dedicated complete settings page for site appearance, module policy, mail, invitation configuration, and future system controls. | Next Product Owner-selected capability. |
| Access, invitations, and roles | Not implemented | No complete User/Invitation/Role persistence, authentication, guarded routes, or authorization workflow exists. | Implement after the settings foundation unless scope is explicitly changed. |
| Recipe ownership and scopes | Not implemented | Recipe has no CLUB/PERSONAL scope or owner; Dish does not expose the approved multi-variant lifecycle. | Release blocker unless explicitly deferred. |
| Recipe publication and moderation | Not implemented | No submission, approval, rejection comment, reviewer, or verified-instructor workflow exists. | Release blocker if shared publication remains in scope. |
| Recipe metadata | Partial | Components, notes, quantity modes, archive state, and equipment exist. Technology, tags, seasons, dietary restrictions, and richer categories are incomplete. | Split into explicit tasks after scope decisions. |
| Consolidated PDF and Excel | Partial | Russian purchase/equipment PDF, Excel, print, and ZIP exist, but the approved consolidated artifacts are incomplete. | Release blocker for specification-complete exports. |
| Audit log | Not implemented | No actor-aware audit persistence or administrator history exists. | Implement after identity. |
| Alcohol prohibition | Not implemented | No centralized backend rule covers Product, Recipe, and CSV import paths. | Release blocker because it is an explicit invariant. |
| Runtime and operator path | Implemented | Installation, update, backup, restore, immutable images, health checks, clean startup, and restart persistence are covered. | Keep as the platform for subsequent slices. |
| Final migration and release gates | Deferred | Basic gates already run; full downgrade/re-upgrade testing should target a feature-frozen schema. | Run after product feature freeze. |

## Product Owner sequencing decision

The next capability is **System Settings foundation**, not multi-user access.

The detailed boundary will be confirmed before implementation. The settings area is expected to provide a dedicated administration page and a durable model for:

- club identity and branding;
- site appearance customization;
- module settings and feature availability;
- invitation-related configuration;
- outbound mail configuration;
- future system settings without creating an unstructured key/value dumping ground.

Actual invitation delivery and user lifecycle may still require the later access foundation. Secrets such as mail passwords must not be returned to the browser or stored as ordinary visible settings.

## Recommended implementation sequence

### 1. System Settings foundation

- define sections, permissions, defaults, validation, secret boundaries, and configuration ownership;
- extend the existing singleton club settings without breaking the document brand snapshot;
- add a dedicated Russian settings page with responsive browser acceptance;
- keep module settings explicit and typed;
- decide which invitation/mail controls are configuration-only and which are functional in the first slice.

### 2. Access foundation

- bootstrap the first administrator safely;
- persist users, invitations, and approved roles;
- implement authentication, sessions, logout, guarded routes, and backend authorization;
- connect invitation behavior to the approved system settings.

### 3. Recipe ownership and lifecycle

- add CLUB and PERSONAL ownership semantics;
- support approved Recipe variants per Dish;
- add submission, approval, rejection, publication, and archive workflows;
- preserve all generator and manual-slot rules.

### 4. Central domain safety

- implement one backend alcohol-prohibition policy across Product, Recipe, and CSV import paths;
- define reviewed handling for existing prohibited records.

### 5. Actor-aware audit log

- persist actor, action, timestamp, target, and safe metadata;
- exclude passwords, tokens, logo bytes, and mail secrets.

### 6. Export completeness

- define the final shared document snapshot;
- complete the approved Russian PDF and workbook sheets;
- keep PDF, Excel, print, and ZIP mutually consistent and branded.

### 7. Product acceptance and feature freeze

- verify active catalogue data and import interaction;
- make explicit optional-scope decisions;
- run end-to-end scenarios for the approved first-release roles and settings;
- freeze feature and schema scope.

### 8. Final release readiness

- run the full PostgreSQL migration cycle on the frozen schema;
- complete the deployment checklist and final release workflow;
- tag only after green exact-head gates.

## Scope controls

- One logical capability per PR.
- Multi-tenancy remains prohibited; one installation represents one club.
- Settings must use typed domain models, not arbitrary unchecked JSON for unrelated modules.
- Secrets must have write-only or external-secret handling and must never appear in exports, logs, or API responses.
- MealSlot and MealSlotDish remain primary persistence; MealPlanItem remains compatibility-only.
- Generator compatibility, ordering, repeatability, archive exclusion, and manual-slot authority remain unchanged.
- Documents remain Russian and use one immutable brand snapshot per generated package.
- No production downgrade is authorized by this audit.

## Definition of done for the audit

- every approved product area has an implementation status;
- release blockers and explicit deferrals are distinguishable;
- the Product Owner-selected System Settings capability is first in the sequence;
- final migration smoke is placed after feature freeze;
- roadmap, status, technical debt, and task index are synchronized;
- full repository Quality passes on the exact audit PR head.
