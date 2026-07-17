# TH-0078 — System Settings Invitation Policy

Status: IN PROGRESS

Last updated: 2026-07-17

## Goal

Add a typed `Приглашения` settings section that stores the future invitation policy before users, tokens, email delivery, and the functional invitation list are implemented.

## Product decisions

- registration remains invitation-only;
- only administrators may manage invitations; this rule is required and cannot be disabled;
- the default invited role is Instructor or Verified Instructor, never Administrator;
- invitation lifetime is configured in days;
- an empty allowed-domain list accepts any email domain;
- configured domains are normalized, deduplicated, and validated by the backend;
- resend permission, active invitation limit, and email-confirmation requirement are stored as future policy;
- saving is section-specific, versioned, row-locked, and recorded in safe history;
- this slice creates no users, invitation records, tokens, emails, sessions, or permissions.

## Scope

### Backend

- add singleton `invitation_settings` persistence with typed columns, version, and timestamp;
- store expiry days, safe default role, allowed email domains, resend policy, active limit, required admin-only flag, and email-confirmation requirement;
- expose GET/PUT/history endpoints under `/api/v1/settings/invitations`;
- reject Administrator as a default invitation role;
- normalize domains to lowercase ASCII without `@`, URL schemes, paths, ports, or duplicates;
- use optimistic versioning, PostgreSQL row lock, HTTP 409 conflicts, and safe focused history;
- add additive Alembic `h10012` and keep one head.

### Frontend

- replace the planned `Приглашения` placeholder with a responsive editor;
- show clearly that functional invitations will arrive with Access foundation;
- edit lifetime, default role, allowed domains, resend, active limit, and email confirmation;
- show the required administrator-only rule as locked with an explanation;
- provide reset, cancel, save, conflict, version, and history states in Russian.

## Out of scope

- User or Invitation persistence;
- token creation, hashing, expiry processing, acceptance, revocation, or resend execution;
- email delivery or SMTP;
- registration, login, sessions, roles, or authorization;
- invitation list, recipient lookup, or audit actors;
- configuration archives.

## Acceptance criteria

- settings persist and reload independently;
- invalid default roles and domains are rejected with clear Russian reasons;
- domain normalization is deterministic and duplicate-free;
- administrator-only cannot be disabled;
- stale writes return HTTP 409 and do not overwrite newer values;
- history stores changed field names only;
- the UI explicitly distinguishes policy preparation from working invitations;
- mobile layout has no horizontal overflow;
- Alembic has one head `h10012`;
- backend, frontend, browser, PostgreSQL, Docker, document, operator, and exact-head Quality gates pass.
