# TourHub Technical Debt

Status date: 2026-07-17

## Implemented through merged PR #87

- complete guided preparation, persisted shopping/equipment, recalculation, readiness, and Russian document package;
- installation, update, backup, restore, recovery, immutable release images, health checks, API proxy, and restart persistence;
- product completeness audit and release sequencing;
- responsive `/settings` and ADR-014 typed section ownership;
- club settings through `h10008`;
- site appearance through `h10009`;
- document appearance and immutable generation snapshot through `h10010`;
- module visibility and backend/database dependency locks through `h10011`;
- optimistic conflicts, PostgreSQL row locks, and safe local-admin settings history;
- final downgrade/re-upgrade migration smoke deferred until feature freeze.

## Active TH-0078 / draft PR #88

The invitation-policy slice addresses:

- no typed source for invitation expiry, default role, domain restrictions, resend policy, active limit, or email confirmation;
- no explicit security boundary preventing Administrator as an accidental default role;
- no persisted mandatory administrator-only management rule;
- no invitation-policy version/history contract;
- a placeholder-only settings section.

Implemented in the draft slice:

- independent singleton `invitation_settings` model and Alembic `h10012`;
- expiry from 1 to 90 days and active limit from 1 to 1000;
- safe default role limited to Instructor or Verified Instructor;
- bounded homogeneous allowed-domain JSON owned by `InvitationSettings`;
- lowercase IDNA normalization, sorting, deduplication, and rejection of addresses, schemes, paths, ports, whitespace, and invalid labels;
- mandatory administrator-only Pydantic and database constraints;
- resend and email-confirmation policy flags;
- optimistic versioning, row locking, HTTP 409 conflicts, and safe invitation history;
- responsive Russian editor and focused desktop/mobile browser acceptance;
- explicit statement that no users, tokens, mail, or invitation lifecycle exist yet.

## Remaining System Settings debt

### Informative mail boundary before access

- define universal SMTP ownership and non-secret fields;
- define environment/write-only password behavior;
- show configured/available/restart status without exposing a secret;
- do not send mail or persist visible passwords before identity exists.

### Configuration export and import

- versioned JSON plus image files in a validated archive;
- unencrypted archives exclude secrets;
- password-encrypted archives may include explicitly approved secrets;
- encryption, key derivation, integrity, password handling, import preview, and rollback require a dedicated security design.

## Remaining release-blocking product debt

1. Access foundation and functional invitation lifecycle.
2. Working mail delivery connected to identity.
3. Recipe ownership, variants, publication, and moderation.
4. Central backend alcohol prohibition across API and CSV import.
5. Actor-aware audit log.
6. Consolidated Russian PDF and workbook contents.
7. Product acceptance and feature freeze.

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
