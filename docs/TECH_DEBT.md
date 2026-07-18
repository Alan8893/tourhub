# TourHub Technical Debt

Status date: 2026-07-18

## Implemented through merged PR #92

- complete guided preparation, persisted shopping/equipment, recalculation, readiness, and Russian document package;
- installation, update, backup, restore, recovery, immutable release images, health checks, API proxy, and restart persistence;
- product completeness audit and release sequencing;
- complete System Settings foundation through `h10013`;
- initial Administrator, sign-in, and settings permissions through `h10014`;
- operational invitations and invited-user creation through `h10015`;
- user list, explicit roles, activity controls, and optimistic user versions through `h10016`;
- conflict handling, PostgreSQL row locks, and safe settings history;
- final downgrade/re-upgrade migration smoke deferred until feature freeze.

## Active TH-0083 / draft PR #93

The current Access slice closes anonymous preparation access:

- one shared Backend dependency covers project, catalogue, import, menu, shopping, equipment, document, dish, and current recipe router groups;
- Administrator, Instructor, and Verified Instructor retain current preparation workflows;
- public health, initial setup, sign-in, and invitation acceptance remain available;
- administrative settings remain Administrator-only;
- one frontend guard covers the complete preparation route tree and preserves the requested path;
- API structure and role behavior have focused tests;
- browser acceptance covers redirect and return behavior;
- release-runtime persistence smoke performs setup/sign-in before project operations;
- no migration is required; the head stays `h10016`.

## Remaining Access debt

1. Account recovery, verified email change, and an operational recovery procedure.
2. Operational session view, cleanup, and global sign-out.
3. Real actor propagation into focused settings history and the later audit log.
4. User profile editing and safe account deletion/retention policy.
5. Additional same-origin request hardening if deployment expands beyond trusted LAN.
6. Retention and cleanup policy for old invitation rows.
7. Per-project ownership only if later approved.

## Remaining release-blocking product debt

1. **Working mail delivery** — consume saved mail metadata and the external deployment value, verify connection, send the fixed Russian test message, connect invitation delivery, and define retry/failure diagnostics.
2. **Recipe ownership and lifecycle** — CLUB/PERSONAL ownership, variants, submission, review, publication, rejection, and archive, including Verified Instructor distinctions.
3. **Central alcohol prohibition** — one Backend policy across Product, Recipe, and CSV import plus existing-record handling.
4. **Actor-aware audit log** — safe real-actor history for project, menu, recipe, settings, mail, user, and role changes.
5. **Consolidated export completeness** — approved complete Russian PDF and workbook sheets using the immutable brand snapshot.
6. **Product acceptance** — active catalogue data, import interaction, optional-scope decisions, and end-to-end scenarios.

## Configuration export and import debt

- versioned JSON plus image files in a validated archive;
- unencrypted archives exclude protected operational values;
- an encrypted archive may include explicitly approved values only after a dedicated design;
- encryption format, integrity, import preview, and rollback remain unimplemented.

## Product Owner decisions still required

- whether preference-based menu priority blocks first release;
- mandatory recipe metadata for first release;
- encrypted settings archive format.

## Deferred final release debt

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- final deployment checklist;
- final release workflow and tag.
