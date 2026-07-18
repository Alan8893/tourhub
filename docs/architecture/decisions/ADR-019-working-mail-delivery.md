# ADR-019 — Working Mail Delivery

Status: Accepted

Date: 2026-07-18

## Context

TourHub already stores typed non-secret SMTP metadata in `MailSettings` and projects only whether the deployment-managed SMTP value exists. Functional invitations already create a valid one-time manual link. The next capability must add connection checks, a fixed test message, and automatic invitation delivery without moving the external SMTP value into PostgreSQL or making user creation depend on an external mail server.

## Decision

### Ownership

- `MailSettings` remains the only owner of non-secret SMTP host, port, connection mode, optional username, sender metadata, test recipient, timeout, and retry count.
- `TOURHUB_SMTP_SECRET` remains deployment-owned environment configuration and is never accepted by application APIs or browser forms.
- `MailDeliveryService` owns network connection, optional authentication, fixed message construction, bounded synchronous retries, and safe result translation.
- Invitation persistence remains owned by `InvitationService`.

### Connection modes

The first-release delivery service uses the Python standard library and supports:

- plain SMTP;
- SMTP upgraded with STARTTLS;
- implicit TLS from connection start.

When no SMTP username is configured, no authentication value is required. When a username is configured, the environment value must also be present.

### Operation order

Invitation create and reissue follow this order:

1. validate policy and create the new invitation transactionally;
2. commit and refresh the invitation;
3. attempt SMTP delivery;
4. return both the delivery outcome and the one-time manual link.

An unavailable or failed delivery must not roll back a valid invitation. Reissue still invalidates the previous link before the delivery attempt, and the replacement manual link is returned even when SMTP fails.

### API results

Connection and delivery operations expose only:

- a bounded status (`sent`, `unavailable`, or `failed` where applicable);
- a Russian operator-safe message;
- attempt count;
- optional recipient address.

The external SMTP value, SMTP transcript, one-time invitation code, and exception details are not returned or stored in settings history.

### Runtime model

Mail operations execute synchronously in the initiating request with the saved timeout and bounded retry count. A queue, background worker, scheduled retry, provider API, HTML-template editor, attachments, bounce processing, and delivery history are separate future capabilities.

## Consequences

- a fresh installation remains healthy without SMTP configuration;
- local no-auth SMTP relays remain supported;
- operators can verify connection and send a fixed Russian test message from System Settings;
- invitation delivery improves convenience without removing the manual recovery path;
- slow or unavailable SMTP is bounded by configured timeout and retries but still occupies the request while it runs;
- future asynchronous delivery can replace the execution mechanism without changing Mail Settings ownership or invitation validity rules.
