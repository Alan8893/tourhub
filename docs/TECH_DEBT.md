# TourHub Technical Debt

Status date: 2026-07-17

## Implemented through merged PR #83

- complete guided project preparation from creation through branded documents;
- persisted shopping, equipment, overrides, recalculation, and reload-safe readiness;
- singleton club branding through Alembic `h10007`;
- installation, update, backup, restore, and recovery runbooks;
- production-like Docker images and release Compose;
- internal PostgreSQL/Redis networking, health checks, API proxy, clean startup, and restart persistence;
- general, document, guided-release, operator, backup/restore, and Docker runtime gates;
- evidence-based product completeness and release sequencing;
- final downgrade/re-upgrade migration smoke deferred until first-release feature freeze.

## Active TH-0074 / draft PR #84

The first System Settings debt slice addresses:

- no dedicated `/settings` surface;
- club settings embedded inside project preparation;
- club identity limited to one required name and one logo;
- no optimistic conflict detection;
- no focused settings-change history;
- no prepared image slots for light/dark themes, favicon, login, or document appearance;
- no explicit typed ownership model for future settings domains.

Implemented in the draft slice:

- typed singleton club identity with one required and multiple optional fields;
- seven validated image roles using PNG/JPEG/WebP and no SVG;
- additive Alembic `h10008`;
- versioned updates with HTTP 409 stale-write protection;
- safe local-admin history retaining the latest 200 records;
- separate responsive settings page and future-section boundaries;
- legacy club-branding and document snapshot compatibility;
- ADR-014 typed settings ownership.

## Remaining System Settings debt

### Site appearance

- global light and dark design tokens;
- organization colors, text, surfaces, navigation, typography, density, shape, buttons, cards, and shadows;
- automatic derived states and contrast validation with an explanation of rejected combinations;
- personal light/dark/system choice in local storage before users and `UserPreferences` later;
- isolated preview, defaults, reset, and safe theme import/export;
- no arbitrary custom CSS.

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
- secrets must remain excluded from logs, history, diagnostics, normal API responses, and unencrypted exports.

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
