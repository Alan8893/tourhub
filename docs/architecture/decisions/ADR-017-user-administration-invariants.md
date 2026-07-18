# ADR-017 — User Administration Invariants

Status: Accepted

Date: 2026-07-18

## Context

TourHub now creates users through Administrator bootstrap and accepted invitations. The next Access slice must support role and activity changes without allowing concurrent edits or an operator mistake to remove all Administrator access from a local installation.

## Decision

- Backend is the authoritative owner of user roles and active state.
- Only an authenticated Administrator may list or update users.
- Each `User` has a positive optimistic `version`; updates require `expected_version` and stale writes return HTTP 409.
- A user update locks the ordered user set before evaluating invariants and applying changes.
- At least one active Administrator must always remain.
- Deactivating a user revokes every active server session for that user in the same transaction.
- Role changes take effect on the next authorized request because Backend resolves the current `User` from the server session.
- Self-demotion or self-deactivation is allowed only when another active Administrator remains.
- Account deletion, password reset, email change, and self-service profile editing are separate future capabilities.
- Frontend confirmation improves UX but never replaces Backend enforcement.

## Consequences

- User updates are serialized, which is acceptable for one local club and a small user set.
- A stale browser cannot overwrite a newer role or activity change.
- An inactive user cannot keep using an existing session.
- Operators must create or promote a second active Administrator before disabling or demoting the first.
- Broader project/catalogue/preparation authorization remains a separate Access slice.
