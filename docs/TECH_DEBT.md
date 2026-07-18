# TourHub Technical Debt

Status date: 2026-07-18

## Implemented through PR #95

- complete guided preparation, persisted shopping/equipment, recalculation, readiness, and Russian document package;
- installation, update, backup, restore, recovery, release images, health checks, API proxy, and restart persistence;
- complete typed System Settings foundation through `h10013`;
- initial Administrator, sign-in, and settings permissions through `h10014`;
- operational invitations and invited-user creation through `h10015`;
- user list, explicit roles, activity controls, and optimistic user versions through `h10016`;
- authenticated preparation routes and APIs for all three approved active roles;
- Administrator-only settings, invitation management, and user administration;
- working SMTP connection check, fixed Russian test message, and best-effort invitation delivery with manual fallback;
- multiple independent sessions per user with current-role propagation on every request;
- complete active-session revocation when a user is deactivated;
- centralized frontend handling for protected HTTP 401 responses;
- exact route return through sign-in and explicit logout;
- visible current user role in the common application header;
- conflict handling, PostgreSQL row locks, safe settings history, and deferred final downgrade/re-upgrade smoke.

TH-0085 implementation head `4879e6dc701550935eb4d173e5098de85d264fd5` passed Quality #835, Document Quality #452, Guided Release Acceptance #403, Operator Docs #389, and Docker Release Runtime #384.

## Remaining Access debt

1. Account recovery, verified email change, and an operational recovery procedure.
2. Operational session view, individual revocation, cleanup, and global sign-out.
3. Real actor propagation into focused settings history and the later audit log.
4. User profile editing and safe account deletion/retention policy.
5. Additional same-origin request hardening if deployment expands beyond trusted LAN.
6. Retention and cleanup policy for old invitation rows.
7. Per-project ownership only if later approved.
8. Live collaborative editing only if later product requirements justify it.

## Remaining mail debt

1. Asynchronous queue and background worker if synchronous latency becomes unacceptable.
2. Scheduled retries, operator delivery history, and failure dashboards.
3. Bounce/complaint handling and provider-specific diagnostics.
4. Approved HTML templates, localization beyond fixed Russian first-release messages, and attachments.
5. Password-reset and account-recovery mail after recovery policy is designed.
6. Explicit public-origin configuration if deployments later terminate proxies in a way that does not preserve the external host.

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
