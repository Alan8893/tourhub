# ADR-015 — Administrator Bootstrap and Server-Owned Sessions

Status: Accepted

Date: 2026-07-18

## Context

TourHub is a local single-club application that now needs operational identity before functional invitations and broader authorization can be implemented. The first installation has no user who can invite another user, so it requires a constrained bootstrap path. Browser-stored bearer tokens would expose long-lived credentials to JavaScript, while a full external identity provider or OAuth deployment is disproportionate for the approved trusted-LAN MVP.

## Decision

### One-time bootstrap

- a singleton `IdentityState` row is created by migration;
- bootstrap locks that row transactionally;
- bootstrap is available only while no user exists and the state is incomplete;
- the created user always has role `Administrator`;
- later users must enter through the functional invitation and administration flows.

### Password handling

- passwords are between 12 and 128 characters in this slice;
- Backend hashes passwords with standard-library `scrypt`, a random per-password salt, and encoded parameters;
- plaintext passwords are never persisted, returned, logged, or added to history;
- invalid login uses one generic response regardless of whether the email exists.

### Session handling

- login and bootstrap generate a cryptographically random opaque token;
- the browser receives it only in an HttpOnly, SameSite=Lax cookie;
- PostgreSQL stores only a SHA-256 token hash plus user, expiry, revocation, creation, and last-seen metadata;
- session lookup, expiry, active-user state, and revocation are enforced by Backend;
- logout revokes the server row and clears the cookie;
- cookie `Secure` is deployment-configurable because the approved local release path may initially use trusted-LAN HTTP, while HTTPS deployments must enable it.

### Authorization boundary in TH-0080

- every System Settings API requires an authenticated Administrator;
- `/settings` is guarded in the frontend and hidden from non-Administrators;
- Backend authorization remains authoritative;
- project, catalogue, import, menu, shopping, equipment, and document routes remain outside this first slice and receive explicit authorization in follow-up work.

## Consequences

- TourHub gains operational identity without pretending invitations already work;
- normal JavaScript cannot read the session token;
- database disclosure does not directly disclose reusable raw session tokens;
- sessions can be expired or revoked independently of browser state;
- functional invitations can create Instructor or Verified Instructor users against the same user/session model;
- broader authorization and request-forgery hardening remain explicit follow-up work.

## Rejected alternatives

- default hard-coded administrator credentials;
- plaintext or reversible password storage;
- localStorage bearer tokens;
- stateless JWTs without server revocation state;
- allowing repeated bootstrap;
- protecting only the frontend while leaving settings APIs public;
- introducing multi-tenancy or an external identity service for the local MVP.
