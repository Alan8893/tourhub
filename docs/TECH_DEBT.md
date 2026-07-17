# TourHub Technical Debt

Status date: 2026-07-17

## Implemented through merged PR #85

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
- independent site appearance through Alembic `h10009`;
- dynamic light/dark MUI themes, presets, isolated preview, and local display mode;
- validated versioned theme JSON import/export without secrets;
- optimistic conflict detection, PostgreSQL row locking, and safe local-admin settings history;
- ADR-014 independent typed settings ownership.

## Active TH-0076 / draft PR #86

The document-appearance slice addresses:

- document branding limited to club name and main logo;
- fixed PDF/Excel heading, table, footer, and density styling;
- no independent document palette or logo selection;
- no contact, custom footer, or title-background controls;
- no document-specific settings API or history;
- no explicit combined club/document snapshot contract.

Implemented in the draft slice:

- independent typed singleton `document_appearance_settings` model and Alembic `h10010`;
- validated primary/accent/heading/title/table palette;
- approved image-source selection with predictable fallback and explicit no-logo mode;
- optional club contacts, custom footer, title image, and comfortable/compact tables;
- backend minimum table-header contrast validation with a Russian reason;
- optimistic versioning, row locking, HTTP 409 conflicts, and safe document history;
- one frozen snapshot loaded once per generation request;
- the same snapshot reused by purchase/equipment PDF, Excel, print, and every ZIP entry;
- centralized ReportLab/openpyxl styling helpers;
- responsive document settings editor with isolated preview, reset, cancel, and save;
- compatibility for existing endpoints, filenames, content types, and legacy `ClubBrandingDTO` construction.

## Remaining System Settings debt

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
   - approved complete Russian PDF and workbook sheets using the implemented immutable brand snapshot.
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
