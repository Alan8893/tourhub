# TH-0084 — Working Mail Delivery

Status: DONE

Completed: 2026-07-18

Merged PR: #94 (`3c51d4c1d0bb0bd96d23a1f4ace0947ae48e9101`)

## Goal

Turn the existing typed mail configuration into an operational delivery capability without storing deployment-managed SMTP values in PostgreSQL.

## Delivered

### Backend

- standard-library SMTP delivery service;
- plain, STARTTLS, and implicit TLS connections;
- optional authentication only when an SMTP username is configured;
- deployment-managed value read only from `TOURHUB_SMTP_SECRET`;
- Administrator-only connection check and fixed Russian test-message endpoints;
- invitation create/reissue attempts automatic delivery after the invitation transaction commits;
- valid invitations and manual links remain available when delivery is unavailable or fails;
- safe delivery status and bounded synchronous retries;
- no migration; Alembic remains at `h10016`.

### Frontend and operations

- connection-check and test-message actions in Mail Settings;
- sent, unavailable, and failed delivery states;
- invitation-delivery status with permanent copy-link fallback;
- responsive browser coverage;
- operator documentation for SMTP environment and network requirements;
- deterministic local fake-SMTP tests without an external paid service.

## Preserved boundaries

- SMTP deployment values are not stored in PostgreSQL or browser state;
- no arbitrary template editor, attachments, queue, background worker, scheduled retry, bounce handling, or provider-specific API;
- password reset and account-recovery mail remain deferred;
- multi-tenancy remains prohibited.

## Verification

Exact PR head `52d0333b807efc891ec8124995c00be3b8bb68ae` passed:

- Quality #832;
- Document Quality #450;
- Guided Release Acceptance #401;
- Operator Docs #387;
- Docker Release Runtime #382.
