# TourHub Technical Debt

Status date: 2026-07-17

## Implemented through merged PR #88

- complete guided preparation, persisted shopping/equipment, recalculation, readiness, and Russian document package;
- installation, update, backup, restore, recovery, immutable release images, health checks, API proxy, and restart persistence;
- product completeness audit and release sequencing;
- responsive `/settings` and ADR-014 typed section ownership;
- club settings through `h10008`;
- site appearance through `h10009`;
- document appearance and immutable generation snapshot through `h10010`;
- module visibility and backend/database dependency locks through `h10011`;
- future invitation policy through `h10012` without users, tokens, or invitation lifecycle;
- optimistic conflicts, PostgreSQL row locks, and safe local-admin settings history;
- final downgrade/re-upgrade migration smoke deferred until feature freeze.

## Active TH-0079 / draft PR #89

The informative mail-boundary slice addresses:

- no typed owner for future universal SMTP parameters;
- no explicit persistence rule separating connection metadata from the external credential;
- no API status contract for environment configuration;
- a placeholder-only `Почта` section;
- no operator documentation for the future environment boundary.

Implemented in the draft slice:

- independent typed singleton `mail_settings` model and additive Alembic `h10013`;
- host, port, plain/STARTTLS/TLS mode, optional username, sender email/name, Reply-To, test recipient, timeout, and retry count;
- backend normalization/validation and database range/mode checks;
- optimistic versioning, row lock, HTTP 409 conflicts, and safe mail history;
- `TOURHUB_SMTP_SECRET` environment source with configured/not-configured status only;
- no credential column, request field, normal response value, UI input, log value, or history value;
- delivery and test-delivery flags remain false;
- responsive Russian editor with disabled test action;
- development/release Compose and installation-runbook coverage.

## Remaining release-blocking product debt

1. **Access foundation**
   - administrator bootstrap, users, functional invitations, approved roles, authentication, sessions, guarded routes, and backend authorization.
2. **Working mail delivery**
   - consume saved mail metadata and the external SMTP credential;
   - verify connection and credentials;
   - send the fixed Russian test message to the configured test recipient;
   - connect delivery to functional invitations;
   - define retry execution, failure status, and safe operational diagnostics.
3. **Recipe ownership and lifecycle**
   - CLUB/PERSONAL ownership, variants, submission, review, publication, rejection, and archive.
4. **Central alcohol prohibition**
   - one backend policy across Product, Recipe, and CSV import plus existing-record handling.
5. **Actor-aware audit log**
   - safe real-actor history for project, menu, recipe, settings, mail, user, and role changes.
6. **Consolidated export completeness**
   - approved complete Russian PDF and workbook sheets using the immutable brand snapshot.
7. **Product acceptance**
   - active catalogue data, import interaction, optional-scope decisions, and end-to-end scenarios.

## Configuration export and import debt

- versioned JSON plus image files in a validated archive;
- unencrypted archives exclude every credential;
- a password-encrypted archive may include explicitly approved values only after a dedicated security design;
- encryption, key derivation, authenticated integrity, password handling, import preview, and rollback remain unimplemented.

## Product Owner decisions still required

- whether preference-based menu priority blocks first release;
- mandatory recipe metadata for first release;
- exact authentication/session mechanism;
- encrypted settings archive cryptographic format.

## Deferred final release debt

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- final deployment checklist;
- final release workflow and tag.
