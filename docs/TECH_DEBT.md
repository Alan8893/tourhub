# TourHub Technical Debt

Status date: 2026-07-18

## Implemented through merged PR #89

- complete guided preparation, persisted shopping/equipment, recalculation, readiness, and Russian document package;
- installation, update, backup, restore, recovery, immutable release images, health checks, API proxy, and restart persistence;
- product completeness audit and release sequencing;
- complete pre-access System Settings foundation through `h10013`;
- typed club, appearance, document, module, invitation-policy, and mail-metadata ownership;
- external SMTP value boundary without delivery;
- optimistic conflicts, PostgreSQL row locks, and safe local-admin settings history;
- final downgrade/re-upgrade migration smoke deferred until feature freeze.

## Active TH-0080 / draft PR #90

The first Access slice addresses:

- no operational user identity;
- no safe one-time Administrator bootstrap;
- no password hashing contract;
- no server-owned session lifecycle;
- no login/logout/current-user API;
- unrestricted System Settings API and route access;
- no authenticated identity in the application shell.

Implemented in the draft slice:

- singleton bootstrap state plus typed users and sessions in additive Alembic `h10014`;
- Administrator, Instructor, and Verified Instructor role values, with bootstrap limited to Administrator;
- standard-library `scrypt` password hashing with random salts;
- opaque random HttpOnly SameSite session cookie and server-side SHA-256 token hash;
- session expiry, revocation, bootstrap status, bootstrap, login, logout, and current-user endpoints;
- generic invalid-login response;
- Administrator dependency on all System Settings APIs;
- guarded `/settings`, responsive bootstrap/login UI, identity display, logout, and post-login settings reload;
- focused API and browser acceptance.

## Remaining access debt

1. Functional invitation rows, token lifecycle, acceptance, resend, revocation, expiry processing, and policy consumption.
2. User list, activation/deactivation, role changes, profile editing, and password reset.
3. Authorization matrix for project, catalogue, import, menu, shopping, equipment, and document operations.
4. Guarded preparation routes and backend mutation enforcement beyond System Settings.
5. Session maintenance policy: cleanup job, global sign-out, password-change invalidation, and operational session view.
6. Real actor propagation into focused settings history and the later consolidated audit log.
7. Request-forgery hardening decision if deployment expands beyond same-origin trusted-LAN use.

## Remaining release-blocking product debt

1. **Access foundation continuation** — invitations, user management, broader authorization, and actor identity.
2. **Working mail delivery** — consume saved mail metadata and the external SMTP value, verify connection, send the fixed Russian test message, connect invitations, and define retry/failure diagnostics.
3. **Recipe ownership and lifecycle** — CLUB/PERSONAL ownership, variants, submission, review, publication, rejection, and archive.
4. **Central alcohol prohibition** — one backend policy across Product, Recipe, and CSV import plus existing-record handling.
5. **Actor-aware audit log** — safe real-actor history for project, menu, recipe, settings, mail, user, and role changes.
6. **Consolidated export completeness** — approved complete Russian PDF and workbook sheets using the immutable brand snapshot.
7. **Product acceptance** — active catalogue data, import interaction, optional-scope decisions, and end-to-end scenarios.

## Configuration export and import debt

- versioned JSON plus image files in a validated archive;
- unencrypted archives exclude every credential;
- a password-encrypted archive may include explicitly approved values only after a dedicated security design;
- encryption, key derivation, authenticated integrity, password handling, import preview, and rollback remain unimplemented.

## Product Owner decisions still required

- whether preference-based menu priority blocks first release;
- mandatory recipe metadata for first release;
- encrypted settings archive cryptographic format.

## Deferred final release debt

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- final deployment checklist;
- final release workflow and tag.
