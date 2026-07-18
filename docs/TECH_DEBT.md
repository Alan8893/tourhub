# TourHub Technical Debt

Status date: 2026-07-18

## Implemented through merged PR #91

- complete guided preparation, persisted shopping/equipment, recalculation, readiness, and Russian document package;
- installation, update, backup, restore, recovery, immutable release images, health checks, API proxy, and restart persistence;
- product completeness audit and release sequencing;
- complete System Settings foundation through `h10013`;
- typed club, appearance, document, module, invitation-policy, and mail-metadata ownership;
- first Administrator bootstrap, protected sign-in sessions, and System Settings authorization through `h10014`;
- operational invitation lifecycle and invited-user creation through `h10015`;
- optimistic conflicts, PostgreSQL row locks, and safe settings history;
- final downgrade/re-upgrade migration smoke deferred until feature freeze.

## Active TH-0082 / draft PR #92

The current Access slice addresses:

- no Administrator-owned user list;
- no explicit role or active-state updates;
- no user-level optimistic version;
- no protection against removing the final active Administrator;
- no immediate session invalidation when an account is disabled;
- no responsive operational user-administration surface.

Implemented in the draft slice:

- additive Alembic `h10016` and positive user versions;
- Administrator-only list and update endpoints;
- explicit Administrator, Instructor, and Verified Instructor role changes;
- activation and deactivation;
- row-locked last-active-Administrator invariant;
- session revocation on deactivation;
- HTTP 409 stale-update handling;
- responsive `Пользователи` cards and explicit confirmation for risky changes;
- backend regression tests and dedicated Chrome acceptance.

## Remaining access debt

1. Authorization matrix for project, catalogue, import, menu, shopping, equipment, and document operations.
2. Guarded preparation routes and backend mutation enforcement beyond System Settings.
3. Account recovery: password reset, verified email change, and operational recovery procedure.
4. Session maintenance: cleanup, global sign-out, account-change invalidation policy, and operational session view.
5. Real actor propagation into focused settings history and the later consolidated audit log.
6. User profile editing and safe account deletion/retention policy.
7. Additional same-origin request hardening if deployment expands beyond trusted-LAN use.
8. Automatic invitation mail and delivery diagnostics once working mail exists.
9. Retention and cleanup policy for old invitation rows.

## Remaining release-blocking product debt

1. **Access foundation continuation** — broader authorization and actor identity.
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
