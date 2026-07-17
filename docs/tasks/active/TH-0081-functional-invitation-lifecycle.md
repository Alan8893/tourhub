# TH-0081 — Functional Invitation Lifecycle

Status: IN PROGRESS

Last updated: 2026-07-18

## Goal

Turn the existing invitation policy into an operational, server-authoritative invitation lifecycle for one local TourHub club without introducing SMTP delivery or broad user administration.

## Scope

### Backend

- add typed Invitation persistence and additive Alembic `h10015` while retaining one head;
- let Administrators create, list, revoke and reissue invitations;
- store only a SHA-256 token hash and return the raw token only in the immediate create/reissue response;
- enforce active-invitation limits, allowed email domains, expiry and safe Instructor/Verified Instructor roles from `InvitationSettings`;
- expose public invitation inspection and acceptance endpoints;
- atomically create one active User and consume the invitation;
- reject expired, revoked, consumed or superseded tokens with non-ambiguous Russian errors;
- keep SMTP delivery unavailable and treat reissue as generation of a new copyable link.

### Frontend

- extend the Administrator invitation settings section with active invitation management;
- provide create, copy-link, reissue and revoke actions;
- add a responsive public acceptance route with display-name and password fields;
- sign the newly created user in after successful acceptance;
- clearly state that links must currently be delivered manually.

## Out of scope

- SMTP delivery, templates, queues or automatic resend;
- full user list, activation/deactivation, role editing or password reset;
- broad preparation-route/API authorization;
- Administrator invitations, self-service registration, external identity or multi-tenancy.

## Acceptance criteria

- only an authenticated Administrator can create/list/reissue/revoke invitations;
- raw invitation tokens are absent from PostgreSQL and normal list/history responses;
- create/reissue returns the raw token exactly once;
- policy limits, domains, expiry and roles are enforced by Backend;
- acceptance creates exactly one User and consumes the invitation atomically;
- concurrent or repeated acceptance cannot create duplicate users;
- revoked, expired, consumed and superseded tokens cannot be accepted;
- public acceptance UX works on desktop/mobile and signs in the accepted user;
- Alembic has one head `h10015`;
- exact-head Quality, document, operator, guided acceptance, PostgreSQL and Docker gates pass.
