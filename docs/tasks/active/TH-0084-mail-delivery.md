# TH-0084 — Working Mail Delivery

Status: IN PROGRESS

Last updated: 2026-07-18

## Goal

Turn the existing typed mail configuration into an operational delivery capability without storing deployment-managed SMTP values in PostgreSQL.

## Scope

### Backend

- add one SMTP delivery service using the Python standard library;
- support plain, STARTTLS, and implicit TLS connections;
- authenticate only when an SMTP username is configured;
- read the deployment-managed value only from `TOURHUB_SMTP_SECRET`;
- expose Administrator-only connection check and fixed Russian test-message endpoints;
- make invitation create/reissue attempt automatic delivery after the invitation transaction commits;
- keep the invitation and manual link available when delivery is unavailable or fails;
- return only safe delivery status and messages without server credentials or raw protocol diagnostics;
- honor configured timeout and retry count.

### Frontend

- enable connection check and test-message actions in Mail Settings;
- show sending, success, unavailable, and safe failure states;
- update invitation management to show whether automatic delivery succeeded and preserve the copy-link fallback;
- keep all mail and invitation administration Administrator-only and responsive.

### Operations

- document the existing environment value and SMTP network requirements;
- keep fresh startup valid when SMTP is not configured;
- add deterministic tests with a local fake SMTP server; no external paid service is required.

## Out of scope

- storing SMTP values in the database or browser;
- HTML template editor, arbitrary templates, attachments, queues, scheduled retries, bounce handling, or provider-specific APIs;
- password reset and account recovery mail;
- background workers or Redis mail queues;
- multi-tenancy.

## Acceptance criteria

- API never accepts or returns the SMTP deployment value;
- connection check works without sending a message;
- the fixed Russian test message reaches the configured test address;
- invitation create/reissue reports automatic delivery status and always retains a manual link;
- a delivery failure does not roll back a valid invitation;
- exact-head Quality, document, operator, guided acceptance, PostgreSQL, and Docker gates pass.