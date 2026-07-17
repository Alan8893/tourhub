# TH-0079 — System Settings Mail Boundary

Status: IN PROGRESS

Last updated: 2026-07-17

## Goal

Add a typed `Почта` settings section that stores approved non-secret future SMTP parameters and exposes a safe environment-secret status without sending email before identity and access exist.

## Product decisions

- future delivery uses universal SMTP;
- non-secret connection and sender parameters may be stored now;
- the SMTP password is never accepted by this settings API and is never stored in PostgreSQL;
- the future secret source is the `TOURHUB_SMTP_PASSWORD` environment variable or another dedicated write-only integration introduced later;
- normal API responses expose only whether the external secret is configured, never its value;
- test delivery remains unavailable until Access foundation and working mail delivery are implemented;
- the first future template is a fixed Russian test message sent to a separately configured test recipient;
- saving is section-specific, versioned, row-locked, and recorded in safe history.

## Scope

### Backend

- add singleton `mail_settings` persistence with typed non-secret columns, version, and timestamp;
- store SMTP host, port, security mode, optional username, sender email/name, optional Reply-To, test recipient, timeout, and retry count;
- expose GET/PUT/history endpoints under `/api/v1/settings/mail`;
- expose `password_configured`, `password_source`, and `delivery_available` as derived read-only status fields;
- reject any password-like request field through the typed schema boundary;
- use optimistic versioning, PostgreSQL row lock, HTTP 409 conflicts, and safe focused history;
- add additive Alembic `h10013` and keep one head.

### Frontend

- replace the planned `Почта` placeholder with a responsive editor;
- show clearly that email delivery and credential verification are not operational yet;
- edit approved non-secret parameters only;
- show environment-secret status without displaying or accepting the secret;
- render a disabled `Отправить тестовое письмо` action with an explanation;
- provide reset, cancel, save, conflict, version, and history states in Russian.

## Out of scope

- SMTP connection attempts, credential checks, message rendering, queues, retries, or delivery;
- password storage, password input, password echo, or password history;
- users, sessions, authentication, roles, authorization, or functional invitations;
- secret rotation UI, encrypted configuration archives, or provider-specific integrations.

## Acceptance criteria

- non-secret settings persist and reload independently;
- invalid host, port, email, timeout, retry, or security values are rejected clearly;
- password-like request fields are rejected and no secret value is returned;
- environment-secret status is derived at request time;
- stale writes return HTTP 409 and do not overwrite newer values;
- history stores changed field names only and excludes addresses or secret values;
- the UI distinguishes saved configuration from unavailable delivery;
- mobile layout has no horizontal overflow;
- Alembic has one head `h10013`;
- backend, frontend, browser, PostgreSQL, Docker, document, operator, and exact-head Quality gates pass.
