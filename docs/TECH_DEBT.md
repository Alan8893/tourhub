# TourHub Technical Debt

Status date: 2026-07-18

## Implemented through merged PR #90

- complete guided preparation, persisted shopping/equipment, recalculation, readiness, and Russian document package;
- installation, update, backup, restore, recovery, immutable release images, health checks, API proxy, and restart persistence;
- product completeness audit and release sequencing;
- complete System Settings foundation through `h10013`;
- typed club, appearance, document, module, invitation-policy, and mail-metadata ownership;
- external mail-value boundary without delivery;
- first Administrator bootstrap, protected sign-in sessions, and System Settings authorization through `h10014`;
- optimistic conflicts, PostgreSQL row locks, and safe settings history;
- final downgrade/re-upgrade migration smoke deferred until feature freeze.

## Active TH-0081 / draft PR #91

The current Access slice adds:

- typed operational invitation records and additive Alembic `h10015`;
- Administrator create, list, repeat-issue, and revoke actions;
- one-time links whose reusable source value is not retained in PostgreSQL;
- Backend enforcement of allowed domains, expiry, active limits, safe roles, and repeat-issue policy;
- explicit active, expired, revoked, accepted, and replaced states;
- atomic creation and initial sign-in of Instructor or Verified Instructor users;
- manual copy-link delivery without mail-service dependency;
- responsive settings management and public acceptance UX;
- focused API regression coverage and production TypeScript build.

## Remaining access debt

1. User list, activation/deactivation, explicit role changes, profile editing, and account recovery.
2. Authorization matrix for project, catalogue, import, menu, shopping, equipment, and document operations.
3. Guarded preparation routes and backend mutation enforcement beyond System Settings.
4. Session maintenance: cleanup, global sign-out, account-change invalidation, and operational session view.
5. Real actor propagation into focused settings history and the later consolidated audit log.
6. Additional same-origin request hardening if deployment expands beyond trusted-LAN use.
7. Automatic invitation mail and delivery diagnostics once working mail exists.
8. Retention and cleanup policy for old accepted, revoked, replaced, and expired invitation rows.

## Remaining release-blocking product debt

1. **Access foundation continuation** — user management, broader authorization, and actor identity.
2. **Working mail delivery** — consume saved mail metadata and the external deployment value, verify connection, send the fixed Russian test message, connect invitation delivery, and define retry/failure diagnostics.
3. **Recipe ownership and lifecycle** — CLUB/PERSONAL ownership, variants, submission, review, publication, rejection, and archive.
4. **Central alcohol prohibition** — one backend policy across Product, Recipe, and CSV import plus existing-record handling.
5. **Actor-aware audit log** — safe real-actor history for project, menu, recipe, settings, mail, user, and role changes.
6. **Consolidated export completeness** — approved complete Russian PDF and workbook sheets using the immutable brand snapshot.
7. **Product acceptance** — active catalogue data, import interaction, optional-scope decisions, and end-to-end scenarios.

## Configuration export and import debt

- versioned JSON plus image files in a validated archive;
- unencrypted archives exclude protected operational values;
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
