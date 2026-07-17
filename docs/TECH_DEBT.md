# TourHub Technical Debt

Status date: 2026-07-17

## Implemented through merged PR #84

- complete guided project preparation from creation through branded documents;
- persisted shopping, equipment, overrides, recalculation, and reload-safe readiness;
- installation, update, backup, restore, and recovery runbooks;
- production-like Docker images and release Compose;
- internal PostgreSQL/Redis networking, health checks, API proxy, clean startup, and restart persistence;
- evidence-based product completeness and release sequencing;
- final downgrade/re-upgrade migration smoke deferred until first-release feature freeze;
- dedicated `/settings` surface and responsive section navigation;
- typed singleton club identity through Alembic `h10008`;
- seven validated club image roles using PNG/JPEG/WebP and no SVG;
- optimistic conflict detection, PostgreSQL row locking, and safe local-admin settings history;
- ADR-014 independent typed settings ownership.

## Active TH-0075 / draft PR #85

The site-appearance slice addresses:

- no organization-wide light and dark theme persistence;
- static one-time MUI theme creation;
- no safe font, density, radius, button/card, or shadow controls;
- no personal system/light/dark preference before user accounts;
- no preview, reset, copy, or safe theme import/export;
- no backend accessibility gate for unreadable color combinations.

Implemented in the draft slice:

- independent typed singleton `appearance_settings` model and Alembic `h10009`;
- complete light and dark token sets plus four built-in presets;
- global dynamic MUI theme application without restart;
- localStorage-only personal display mode until `UserPreferences` exists;
- isolated preview that never applies an unsaved draft globally;
- backend #RRGGBB and WCAG-style text/surface contrast validation with a Russian reason;
- typed safe font stacks, density, radius, button/card styles, and shadows;
- reset, cancel, copy, versioned JSON import, and JSON export without secrets;
- optimistic versioning, row locking, HTTP 409 conflicts, and safe appearance history;
- independent desktop/mobile appearance browser acceptance.

## Remaining System Settings debt

### Document appearance

- independent document palette and image selection;
- title, heading, table, footer, contact, title-background, and density settings;
- immutable snapshot shared consistently by PDF, Excel, print, and ZIP;
- explicit migration from the existing main-logo-only document branding.

### Modules and future access configuration

- typed module visibility configuration;
- backend dependency locks for required modules;
- navigation hiding only in the first slice, with direct URL and API behavior unchanged;
- typed invitation policy settings before functional invitation delivery;
- invitation list deferred until access foundation;
- informative mail boundary until identity exists.

### Mail after access foundation

- universal SMTP configuration;
- host, port, TLS/STARTTLS, username, sender, Reply-To, timeout, and retry policy;
- password supplied through environment or another write-only secret boundary;
- configured/verified/restart status without returning the secret;
- separate test-recipient field and fixed Russian test email;
- no visual template editor in the first mail slice.

### Configuration export and import

- versioned JSON plus image files in a validated archive;
- unencrypted archive excludes every secret;
- password-encrypted archive may include explicitly approved secrets;
- encryption, key derivation, authenticated integrity, password handling, import preview, and rollback require a separate security design;
- secrets must remain excluded from logs, history, diagnostics, normal API responses, and unencrypted exports;
- appearance-only JSON export in TH-0075 is intentionally not the full-system archive.

## Remaining release-blocking product debt

1. **Access foundation**
   - users, invitations, approved roles, authentication, sessions, guarded routes, and backend authorization.
2. **Working mail delivery**
   - connect approved mail settings to identity and invitation flows.
3. **Recipe ownership and lifecycle**
   - CLUB/PERSONAL ownership, multiple variants, submission, review, approval, rejection, publication, archive, and generation modes.
4. **Central alcohol prohibition**
   - one backend rule across Product, Recipe, and CSV import plus reviewed existing-record handling.
5. **Actor-aware audit log**
   - safe history for project, menu, recipe, settings, mail, user, and role changes.
6. **Consolidated export completeness**
   - approved complete Russian PDF and workbook sheets using one brand snapshot.
7. **Product acceptance**
   - active catalogue data, import interaction, optional-scope decisions, and end-to-end scenarios.

## Product Owner decisions still required

- whether preference-based menu priority blocks first release;
- mandatory recipe metadata for first release;
- exact authentication/session mechanism during access-foundation design;
- encrypted settings archive cryptographic format during its dedicated security design.

## Deferred final release debt

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- final production-like deployment checklist;
- final release workflow and release tag.
