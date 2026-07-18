# TourHub Technical Debt

Status date: 2026-07-18

## Implemented through TH-0088 / PR #98

- guided preparation, persisted shopping/equipment, recalculation, readiness, and Russian document package;
- production-like runtime, backup/restore, health checks, API proxy, and restart persistence;
- typed System Settings through `h10013`;
- invitation-only Access, roles, users, and multi-session readiness through `h10016`;
- working SMTP invitation delivery with manual fallback;
- Recipe CLUB/PERSONAL ownership and nested authorization through `h10017`;
- Recipe lifecycle and moderation through `h10018`;
- ordered Dish Recipe variants, three Project generation modes, and persisted assignment Recipe snapshots through `h10019`;
- shopping/equipment calculations based on assignment Recipes rather than mutable Dish defaults;
- responsive Dish variant, Project mode, and selected-Recipe UI;
- focused Backend coverage for actor filtering, mode order, deterministic rotation, manual preservation, migration compatibility, and catalogue behavior.

## Remaining Recipe and menu debt

1. Immutable moderation history beyond the latest decision.
2. Optional moderation notifications.
3. Ownership-aware CSV import UX beyond trusted shared-catalogue import.
4. Preparation technology, dietary metadata, season metadata, and richer categories.
5. Decide whether Recipe-level optimistic versions are required beyond serialized lifecycle transitions.
6. Per-meal manual Recipe switching without replacing the Dish.
7. Preference weights or ranking beyond `club_only`, `club_and_personal`, and `personal_preferred`.

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

1. **Central alcohol prohibition** across Product, Recipe, and CSV import, including existing-record handling.
2. **Actor-aware audit log**, including immutable moderation history.
3. **Consolidated export completeness** for the approved PDF and workbook.
4. **Product acceptance and feature freeze**.

## Configuration export/import debt

- versioned validated archive;
- protected-value exclusion from unencrypted exports;
- approved encryption, integrity, preview, and rollback design.

## Product Owner decisions still required

- whether preference weighting beyond the approved generation modes belongs in a later release;
- mandatory Recipe metadata for first release;
- encrypted settings archive format.

## Deferred final release debt

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- final deployment checklist;
- final release workflow and tag.
