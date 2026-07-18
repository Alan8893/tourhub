# TourHub Technical Debt

Status date: 2026-07-18

## Implemented through PR #96 plus draft PR #97

- complete guided preparation, persisted shopping/equipment, recalculation, readiness, and Russian document package;
- installation, update, backup, restore, recovery, release images, health checks, API proxy, and restart persistence;
- complete typed System Settings foundation through `h10013`;
- invitation-only Access foundation and user administration through `h10016`;
- working SMTP connection check, fixed Russian test message, and best-effort invitation delivery with manual fallback;
- multiple independent sessions per user with current-role propagation and complete deactivation revocation;
- centralized frontend handling for protected HTTP 401 responses and exact route return;
- Recipe CLUB/PERSONAL scope, owner identity, visibility filtering, role-aware editing, and nested ownership enforcement through `h10017`;
- draft `h10018` lifecycle states, row-locked submission/moderation transitions, submitter/reviewer attribution, required rejection comment, and capability-driven moderation UI;
- conflict handling, PostgreSQL row locks, safe settings history, and deferred final downgrade/re-upgrade smoke.

PR #96 merged as `d9ee573d44d885b48a2ce9424e9695f25d95a665`. Draft PR #97 is the active TH-0087 slice.

## Remaining recipe lifecycle debt

1. Full immutable moderation history beyond the latest submission and decision fields.
2. Optional moderation notifications after a delivery policy is approved.
3. Multiple Recipe variants per Dish.
4. Club-only, club-plus-personal, and personal-preferred generation modes.
5. Ownership-aware CSV import preview/apply UX beyond trusted shared-catalogue import.
6. Decide whether recipe-level optimistic versions are still needed beyond serialized lifecycle transitions.
7. Preparation technology, dietary metadata, season metadata, and richer categories required by the approved product target.

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

1. **Dish recipe variants and generation modes** — multiple recipes per Dish and approved club/personal selection modes.
2. **Central alcohol prohibition** — one Backend policy across Product, Recipe, and CSV import plus existing-record handling.
3. **Actor-aware audit log** — safe real-actor history for project, menu, recipe, moderation, settings, mail, user, and role changes.
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
