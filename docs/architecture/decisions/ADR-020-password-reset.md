# ADR-020 — Password Reset and Account Recovery

Status: Accepted

Date: 2026-10-20

## Context

TourHub has server-owned sessions, scrypt password hashing, and configured SMTP delivery. Account recovery was previously deferred. Recovery must not disclose whether an email belongs to an account, and possession of a reset link must not grant a permanent session.

## Decision

- Public API uses separate request and confirmation endpoints under `/api/v1/auth/password-reset`.
- The request endpoint always returns HTTP 202 with the same generic message for unknown, inactive, throttled, and eligible accounts.
- A reset token is generated with the cryptographic `secrets` module, stored only as a SHA-256 hash, expires after 30 minutes, and is single-use.
- Issuing a new token consumes all previous unconsumed reset tokens for the same user.
- Successful confirmation updates the password using the existing scrypt password hasher, consumes all reset tokens, and revokes every active session in the same database transaction.
- Request throttling is persistent in PostgreSQL: at most three requests per normalized email in 15 minutes and ten requests per source IP in one hour. Old attempt records are removed during request handling.
- The email link uses the configured `FRONTEND_PUBLIC_URL` and places the raw token in the URL fragment. The API never trusts the incoming Host header to build a reset URL.
- The request endpoint schedules SMTP delivery after returning the generic response. Delivery failures do not change the public response.
- Production deployments must configure `FRONTEND_PUBLIC_URL` to enable recovery delivery; without a valid URL, no token is issued and no email is sent. The development Compose stack defaults to `http://localhost:5173`.

## Consequences

- Reset tokens and account existence are not returned by the public API.
- A successful password reset signs the user out of every active session.
- The public URL must match the address users actually open in their browser.
- Email delivery remains synchronous within the background task; a durable outbox and delivery retries are deferred.
