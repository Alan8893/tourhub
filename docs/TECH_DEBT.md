# TourHub Technical Debt

Status date: 2026-07-18

## Implemented through TH-0087 / PR #97

- guided preparation, persisted shopping/equipment, recalculation, readiness, and Russian document package;
- production-like runtime, backup/restore, health checks, API proxy, and restart persistence;
- typed System Settings through `h10013`;
- invitation-only Access, roles, users, and multi-session readiness through `h10016`;
- working SMTP invitation delivery with manual fallback;
- Recipe CLUB/PERSONAL ownership and nested authorization through `h10017`;
- Recipe lifecycle and moderation through `h10018`: draft, submission, row-locked review, publication, rejection feedback, resubmission, attribution, capability-driven UI, and focused Chrome acceptance.

TH-0087 implementation head `7dd0ddd398b4f4b82d43f30db8c95c0489f2f31b` passed Quality #887, Document Quality #502, Guided Release Acceptance #453, Operator Docs #439, and Docker Release Runtime #434.

## Remaining recipe debt

1. Multiple Recipe variants per Dish.
2. Club-only, club-plus-personal, and personal-preferred generation modes.
3. Immutable moderation history beyond the latest decision.
4. Optional moderation notifications.
5. Ownership-aware CSV import UX beyond trusted shared-catalogue import.
6. Preparation technology, dietary metadata, season metadata, and richer categories.
7. Decide whether recipe-level optimistic versions are required beyond serialized lifecycle transitions.

## Remaining Access and mail debt

- account recovery and verified email change;
- session administration, individual revocation, cleanup, and global sign-out;
- user profile editing and account-retention policy;
- real actor propagation into focused settings history and the later audit log;
- invitation retention and cleanup;
- asynchronous mail delivery, scheduled retries, delivery history, and bounce diagnostics;
- approved mail templates and attachments;
- additional same-origin request hardening if deployment expands beyond trusted LAN.

## Remaining release-blocking product debt

1. **Dish recipe variants and generation modes**.
2. **Central alcohol prohibition** across Product, Recipe, and CSV import.
3. **Actor-aware audit log**, including immutable moderation history.
4. **Consolidated export completeness** for the approved PDF and workbook.
5. **Product acceptance and feature freeze**.

## Configuration export/import debt

- versioned validated archive;
- protected-value exclusion from unencrypted exports;
- approved encryption, integrity, preview, and rollback design.

## Product Owner decisions still required

- whether preference-based menu priority blocks first release;
- mandatory recipe metadata for first release;
- encrypted settings archive format.

## Deferred final release debt

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- final deployment checklist;
- final release workflow and tag.
