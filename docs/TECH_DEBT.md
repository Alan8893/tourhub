# TourHub Technical Debt

Status date: 2026-07-17

## Implemented through merged PR #80

- complete guided project preparation from creation through branded documents;
- persisted shopping, equipment, overrides, recalculation, and reload-safe readiness;
- singleton club branding through Alembic `h10007`;
- installation, update, backup, restore, and recovery runbooks;
- production-like Docker images and release Compose;
- internal PostgreSQL/Redis networking, health checks, API proxy, clean startup, and restart persistence;
- general, document, guided-release, operator, backup/restore, and Docker runtime gates.

## Current completeness and sequencing debt

- the approved product specification is broader than the current single-user runtime;
- final downgrade/re-upgrade migration smoke must run only after first-release feature freeze;
- basic Alembic, PostgreSQL, backup/restore, Docker, and full Quality gates remain mandatory during feature development;
- the next Product Owner-selected capability is System Settings foundation rather than access foundation.

## System Settings debt — next capability

- no unified dedicated settings page exists for all system configuration;
- existing singleton club name/logo settings must be extended without breaking the shared document brand snapshot;
- site appearance controls, allowed theme tokens, preview, defaults, and reset behavior are undefined;
- module settings and their effect on navigation, APIs, and generated documents are undefined;
- invitation-related policy and actual invitation delivery are not yet separated;
- outbound mail provider, sender identity, encryption/write-only secret handling, and test-delivery behavior are undefined;
- future settings require typed ownership and validation rather than arbitrary unchecked key/value storage;
- settings changes will eventually require actor-aware audit coverage.

## Remaining release-blocking product debt

1. **Access foundation**
   - users, invitations, roles, authentication, sessions, guarded routes, and backend authorization.
2. **Recipe ownership and lifecycle**
   - CLUB/PERSONAL ownership, variants, submission, review, approval, rejection, publication, archive, and generation modes.
3. **Central alcohol prohibition**
   - one backend rule across Product, Recipe, and CSV import plus reviewed existing-record handling.
4. **Actor-aware audit log**
   - safe history for project, menu, recipe, settings, user, and role changes.
5. **Consolidated export completeness**
   - approved complete Russian PDF and workbook sheets using one brand snapshot.
6. **Product acceptance**
   - active catalogue data, import interaction, optional-scope decisions, and end-to-end scenarios.

## Product Owner decisions required

- exact sections and first slice of the System Settings page;
- whether appearance uses predefined themes, editable tokens, or both;
- which modules can be disabled and what disabling means;
- whether invitation controls are configuration-only until access foundation;
- SMTP/provider support, secret storage, test email, retries, and failure visibility;
- whether preference-based menu priority blocks first release;
- mandatory recipe metadata for first release.

## Deferred final release debt

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- final production-like deployment checklist;
- final release workflow and release tag.
