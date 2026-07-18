# TourHub Technical Debt

Status date: 2026-07-18

## Implemented through PR #96

- complete guided preparation, persisted shopping/equipment, recalculation, readiness, and Russian document package;
- installation, update, backup, restore, recovery, release images, health checks, API proxy, and restart persistence;
- complete typed System Settings foundation through `h10013`;
- invitation-only Access foundation and user administration through `h10016`;
- working SMTP connection check, fixed Russian test message, and best-effort invitation delivery with manual fallback;
- multiple independent sessions per user with current-role propagation and complete deactivation revocation;
- centralized frontend handling for protected HTTP 401 responses and exact route return;
- Recipe CLUB/PERSONAL scope, owner identity, visibility filtering, role-aware editing, and nested ownership enforcement through `h10017`;
- safe recipe owner/capability projection and responsive ownership UI;
- conflict handling, PostgreSQL row locks, safe settings history, and deferred final downgrade/re-upgrade smoke.

PR #96 implementation head `29b84be3f98a721d8d0faf2fa1908f65681820cd` passed Quality #858, Document Quality #474, Guided Release Acceptance #425, Operator Docs #411, and Docker Release Runtime #406.

## Remaining recipe lifecycle debt

1. Submission and resubmission states for PERSONAL recipes.
2. Verified Instructor and Administrator review queue.
3. Publication transition from PERSONAL to CLUB with an explicit immutable origin policy.
4. Rejection with required comment and visible feedback to the owner.
5. Moderation lifecycle history before the consolidated actor-aware audit exists.
6. Multiple Recipe variants per Dish.
7. Club-only, club-plus-personal, and personal-preferred generation modes.
8. Optimistic recipe versions when lifecycle transitions and concurrent editing are introduced.
9. Ownership-aware CSV import preview/apply UX beyond trusted shared-catalogue import.

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

1. **Recipe publication and moderation** — submission, review, publication, rejection, resubmission, and Verified Instructor distinctions.
2. **Dish recipe variants and generation modes** — multiple recipes per Dish and approved club/personal selection modes.
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
