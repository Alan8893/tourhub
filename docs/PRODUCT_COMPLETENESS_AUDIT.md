# TourHub Product Completeness Audit

Status date: 2026-07-17

## Purpose

This audit compares the approved `PRODUCT_SPEC.md` with the implemented TourHub application after merged PR #83 and records the Product Owner-approved implementation order.

The audit changes sequencing and scope visibility. Runtime implementation is performed in separate capability PRs.

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

- `main`: `950a43914230f6fe4be3bf217a4e5f1b79e7265f` — merged PR #83.
- `main` Alembic head: `h10007`.
- Production-like Docker image build, clean startup, API proxying, health checks, migration head, and restart persistence are validated.
- Current runtime is a local single-club, single-user application.
- Singleton club name and logo settings feed one document brand snapshot.
- Draft PR #84 implements the dedicated settings shell and expanded typed club profile through additive head `h10008`.
- Current frontend access routes remain placeholders; application routes are not protected by an implemented identity workflow.
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
| Club profile and branding | In progress in PR #84 | Existing name/logo branding is expanded into a dedicated typed, versioned club section with optional profile fields and approved image roles. Existing document branding remains compatible. | Complete PR #84 independently. |
| Site appearance | Planned | Static MUI theme has no organization design tokens, light/dark definitions, contrast validation, preview, defaults, or theme import/export. | Next System Settings slice after PR #84. |
| Document appearance | Planned | Existing documents consume one name/logo snapshot but have no independent palette, footer, title background, contact, or density controls. | Separate settings and export slice. |
| Module settings | Planned | No typed navigation-visibility policy or required-module dependency locks exist. | Implement as a separate settings slice; hiding initially affects navigation only. |
| Invitation configuration | Planned | Product Owner approved future policy fields, but no functional invitation list or users exist. | Configure boundaries before access; implement workflow with access foundation. |
| Mail configuration and delivery | Planned after access | Universal SMTP, write-only environment secret, sender identity, test recipient, retries, and status are approved but not implemented. | Implement after multi-user identity exists. |
| Access, invitations, and roles | Not implemented | No complete User/Invitation/Role persistence, authentication, guarded routes, or authorization workflow exists. | Implement after the settings foundation. |
| Recipe ownership and scopes | Not implemented | Recipe has no CLUB/PERSONAL scope or owner; Dish does not expose the approved multi-variant lifecycle. | Release blocker unless explicitly deferred. |
| Recipe publication and moderation | Not implemented | No submission, approval, rejection comment, reviewer, or verified-instructor workflow exists. | Release blocker if shared publication remains in scope. |
| Recipe metadata | Partial | Components, notes, quantity modes, archive state, and equipment exist. Technology, tags, seasons, dietary restrictions, and richer categories are incomplete. | Split into explicit tasks after scope decisions. |
| Consolidated PDF and Excel | Partial | Russian purchase/equipment PDF, Excel, print, and ZIP exist, but the approved consolidated artifacts are incomplete. | Release blocker for specification-complete exports. |
| Audit log | Partial foundation | PR #84 adds focused safe settings history without identity. No actor-aware application audit exists. | Replace local actor label with real identity and implement the broader audit after access. |
| Alcohol prohibition | Not implemented | No centralized backend rule covers Product, Recipe, and CSV import paths. | Release blocker because it is an explicit invariant. |
| Runtime and operator path | Implemented | Installation, update, backup, restore, immutable images, health checks, clean startup, and restart persistence are covered. | Keep as the platform for subsequent slices. |
| Final migration and release gates | Deferred | Basic gates already run; full downgrade/re-upgrade testing should target a feature-frozen schema. | Run after product feature freeze. |

## Approved System Settings decisions

### Architecture

- one responsive `/settings` surface;
- independent typed settings ownership by section;
- `ClubSettings` remains a club-identity singleton rather than a settings god object;
- a bounded typed social-link collection may use JSON, but unrelated settings may not use arbitrary JSON or generic key/value storage;
- sections save independently;
- optimistic version checks reject stale writes;
- settings history retains the latest 200 safe records;
- actor label is `Локальный администратор` until identity exists;
- passwords, tokens, image bytes, data URLs, and future secrets are excluded from history, logs, diagnostics, and normal API responses.

ADR-014 records the complete ownership decision.

### Club profile

- club name is the only required field;
- short/legal names, description, address, phone, email, website, social links, timezone, city, and region are optional;
- images include main/light/dark logos, square icon, favicon, login background, and document image;
- accepted images are PNG, JPEG, and WebP; SVG is rejected;
- light/dark logos fall back to the main logo;
- existing exports continue using the main name/logo snapshot until document appearance is implemented.

### Appearance

- global organization appearance uses validated design tokens rather than arbitrary CSS;
- light and dark themes are required;
- the user chooses only light/dark/system mode;
- the choice uses local storage before users and typed `UserPreferences` after access exists;
- organization colors, typography, density, shape, buttons, cards, and shadows remain global;
- contrast failures are rejected with an explanation;
- an isolated preview is implemented first, with whole-application preview considered after stabilization;
- reset, defaults, copy, and safe import/export are required.

### Documents

Document appearance is separate from site appearance and will control:

- primary/accent colors;
- headings and tables;
- logo choice;
- club contact visibility;
- custom footer;
- title-page background;
- compact or normal table density.

### Modules, invitations, and mail

- initial module disabling hides navigation only;
- required modules cannot be disabled and backend dependencies explain the reason;
- direct URLs and APIs remain available in the first visibility slice;
- invitation policy settings are prepared before users, while the functional invitation list remains access-foundation debt;
- the Mail section is informative until multi-user access exists;
- working mail uses universal SMTP and a password from an external/write-only secret boundary;
- the first mail template is a fixed Russian test message sent to a separate test address.

### Configuration archives

- configuration archives use versioned JSON and separate image files;
- unencrypted archives exclude secrets;
- a password-encrypted archive may include explicitly approved secrets;
- encryption and import safety require a separate security design and PR.

## Recommended implementation sequence

1. Complete PR #84: settings shell and club profile.
2. Implement site appearance and preview.
3. Implement document appearance.
4. Implement module visibility and future invitation/mail configuration boundaries.
5. Implement access foundation and functional invitations.
6. Implement working mail delivery.
7. Implement recipe ownership and lifecycle.
8. Implement central alcohol prohibition.
9. Implement actor-aware audit log.
10. Complete consolidated exports.
11. Run product acceptance and feature freeze.
12. Run final migration and release readiness.

## Scope controls

- One logical capability per PR.
- Multi-tenancy remains prohibited; one installation represents one club.
- Settings use typed domain models, not arbitrary unchecked JSON for unrelated modules.
- Secrets use write-only or external-secret handling and never appear in normal exports, logs, history, or API responses.
- MealSlot and MealSlotDish remain primary persistence; MealPlanItem remains compatibility-only.
- Generator compatibility, ordering, repeatability, archive exclusion, and manual-slot authority remain unchanged.
- Documents remain Russian and use one immutable brand snapshot per generated package.
- No production downgrade is authorized by this audit.
