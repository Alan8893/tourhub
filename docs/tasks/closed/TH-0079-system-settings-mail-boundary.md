# TH-0079 — System Settings Mail Boundary

Status: DONE

Completed: 2026-07-18

Merged PR: #89 (`bff7950e3542b719983f2a09b61b9a901fbaca64`)

## Delivered

- independent typed `MailSettings` and additive Alembic `h10013`;
- validated non-secret SMTP host, port, security, username, sender, Reply-To, test-recipient, timeout, and retry metadata;
- environment-owned `TOURHUB_SMTP_SECRET` status without database, API, UI, history, or log exposure of its value;
- hard-disabled delivery and test-delivery flags until identity and working mail delivery exist;
- optimistic versioning, PostgreSQL row lock, HTTP 409 conflicts, and safe history;
- responsive Russian mail editor and operator documentation;
- exact-head Quality #660, Document Quality #283, Guided Release Acceptance #234, Operator Docs #220, and Docker Release Runtime #215.

## Deferred intentionally

- SMTP connection and credential verification;
- message rendering, queueing, retries, and delivery;
- functional invitations and users;
- secret rotation UI and encrypted configuration archives.
