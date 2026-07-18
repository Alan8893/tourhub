# ADR-016 — One-Time Invitation Links

Status: Accepted

Date: 2026-07-18

## Context

TourHub now has one local Administrator and server-owned sessions. The next Access slice must create Instructor and Verified Instructor users while respecting the typed `InvitationSettings` policy. Working SMTP delivery is intentionally later, so invitation delivery cannot depend on email infrastructure.

## Decision

TourHub uses server-authoritative one-time invitation links.

- Only an authenticated Administrator may create, list, reissue, or revoke invitations.
- An invitation binds one normalized email address and one safe non-Administrator role.
- Backend applies allowed-domain, expiry, active-limit, role, and reissue policy from `InvitationSettings`.
- The raw invitation code is generated with a cryptographically secure random source and returned only in the immediate create or reissue response.
- PostgreSQL stores only a SHA-256 hash of the code; normal list responses never include it.
- Until working mail delivery exists, the Administrator copies and transfers the link manually through an approved channel.
- Reissue creates a new code and permanently supersedes the previous link.
- Revoke permanently disables an active link.
- Public inspection reveals only the bound email, role, and expiry after the code has been validated.
- Acceptance row-locks the invitation, rechecks state and policy, creates one active user, consumes the invitation, and creates the initial server session in one transaction.
- Expired, revoked, consumed, superseded, or unknown codes cannot create a user.
- Administrator invitations and self-service registration remain prohibited.

## Consequences

- SMTP outages cannot block local user onboarding.
- The raw code cannot be recovered from the database or invitation list.
- A copied link is a bearer capability and must be transferred carefully.
- Email ownership is represented by possession of the bound one-time link until real mail delivery is implemented.
- User administration, password reset, broader authorization, and automatic email delivery remain separate capabilities.

## Rejected alternatives

- Storing reusable raw invitation codes in PostgreSQL.
- Allowing the frontend to decide expiry, domains, role, or lifecycle state.
- Reusing the same code during resend/reissue.
- Creating Administrator accounts through invitations.
- Blocking functional invitations until SMTP delivery exists.
