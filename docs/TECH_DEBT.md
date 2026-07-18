# TourHub Technical Debt

Status date: 2026-07-18

## Implemented through merged PR #93

- complete guided preparation, persisted shopping/equipment, recalculation, readiness, and Russian document package;
- installation, update, backup, restore, recovery, release images, health checks, API proxy, and restart persistence;
- complete typed System Settings foundation through `h10013`;
- initial Administrator, sign-in, and settings permissions through `h10014`;
- operational invitations and invited-user creation through `h10015`;
- user list, explicit roles, activity controls, and optimistic user versions through `h10016`;
- authenticated preparation routes and APIs for all three approved active roles;
- Administrator-only settings, invitation management, and user administration;
- conflict handling, PostgreSQL row locks, safe settings history, and deferred final downgrade/re-upgrade smoke.

## Active TH-0084 / draft PR #94

The current mail slice addresses:

- no operational SMTP connection check;
- no fixed test message;
- no automatic invitation delivery;
- no safe delivery status in invitation responses;
- no browser workflow for connection and delivery diagnostics.

Implemented in the draft slice:

- standard-library plain, STARTTLS, and implicit-TLS transport;
- optional username authentication using the deployment-managed environment value;
- saved timeout and bounded synchronous retries;
- Administrator-only connection check and fixed Russian test message;
- best-effort invitation delivery after the invitation transaction commits;
- manual link fallback on unavailable or failed delivery;
- safe result messages without external values, protocol transcript, or one-time codes;
- responsive Mail Settings and invitation-delivery UI;
- deterministic fake-SMTP tests and Chrome acceptance;
- no migration; Alembic remains at `h10016`.

## Remaining mail debt

1. Asynchronous queue and background worker if synchronous latency becomes unacceptable.
2. Scheduled retries, operator delivery history, and failure dashboards.
3. Bounce/complaint handling and provider-specific diagnostics.
4. Approved HTML templates, localization beyond fixed Russian first-release messages, and attachments.
5. Password-reset and account-recovery mail after recovery policy is designed.
6. Explicit public-origin configuration if deployments later terminate proxies in a way that does not preserve the external host.

## Remaining Access debt

1. Account recovery, verified email change, and an operational recovery procedure.
2. Operational session view, cleanup, and global sign-out.
3. Real actor propagation into focused settings history and the later audit log.
4. User profile editing and safe account deletion/retention policy.
5. Additional same-origin request hardening if deployment expands beyond trusted LAN.
6. Retention and cleanup policy for old invitation rows.
7. Per-project ownership only if later approved.

## Remaining release-blocking product debt

1. **Recipe ownership and lifecycle** — CLUB/PERSONAL ownership, variants, submission, review, publication, rejection, archive, and Verified Instructor distinctions.
2. **Central alcohol prohibition** — one Backend policy across Product, Recipe, and CSV import plus existing-record handling.
3. **Actor-aware audit log** — safe real-actor history for project, menu, recipe, settings, mail, user, and role changes.
4. **Consolidated export completeness** — approved complete Russian PDF and workbook sheets using the immutable brand snapshot.
5. **Product acceptance** — active catalogue data, import interaction, optional-scope decisions, and end-to-end scenarios.

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
