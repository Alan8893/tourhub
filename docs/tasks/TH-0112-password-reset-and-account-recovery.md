# TH-0112 — Password Reset and Account Recovery

Status: Implementation in progress

## Goal

Allow existing users to recover account access through the configured SMTP service without exposing account existence or leaving old sessions active.

## Scope

- Public password-reset request and confirmation endpoints.
- Single-use, expiring reset tokens stored only as hashes.
- Persistent email/IP request throttling.
- Trusted configured Frontend URL for reset links.
- Reuse existing SMTP delivery and scrypt password hashing.
- Login link, request form, and reset form.
- Alembic migration and API coverage.

## Acceptance criteria

- [x] Generic request response for known and unknown emails.
- [x] Tokens are cryptographically random, hashed at rest, expire after 30 minutes, and cannot be reused.
- [x] Password update, token invalidation, and session revocation occur transactionally.
- [x] Persistent request throttling is implemented.
- [x] Reset links use `FRONTEND_PUBLIC_URL`, not the request Host header.
- [x] Frontend request/reset routes are registered.
- [ ] Backend and frontend tests executed successfully.
- [ ] Migration cycle and Alembic single-head validation executed.
- [ ] Final review and pull-request checks complete.

## Deployment configuration

Set `FRONTEND_PUBLIC_URL` to the public origin that users open in their browser to enable recovery email delivery. Without a valid value, no reset token is issued and no email is sent. The development Compose stack defaults to `http://localhost:5173`.

SMTP authentication continues to use the deployment-managed `TOURHUB_SMTP_SECRET` when the saved SMTP settings specify a username.
