# TH-0080 — Access Bootstrap and Authentication

Status: IN PROGRESS

Last updated: 2026-07-18

## Goal

Introduce the first operational identity boundary for one local TourHub installation: create the first Administrator exactly once, authenticate with server-owned sessions, and protect System Settings without mixing in the functional invitation lifecycle.

## Scope

### Backend

- add typed User and AuthSession persistence;
- support Administrator, Instructor, and Verified Instructor roles while allowing only Administrator bootstrap in this slice;
- expose public bootstrap-status, one-time bootstrap, login, logout, and current-user endpoints;
- hash passwords with a memory-hard standard-library algorithm and store no plaintext credentials;
- issue opaque random session tokens in HttpOnly SameSite cookies and store only token hashes;
- expire and revoke sessions server-side;
- protect all `/api/v1/settings/...` endpoints with Administrator authorization;
- add additive Alembic `h10014` and retain one head.

### Frontend

- add an authentication provider and startup identity check;
- replace the login placeholder with responsive bootstrap/login UX;
- guard `/settings` and redirect unauthenticated users to `/login`;
- show the authenticated user and logout action in the application shell;
- preserve direct access to existing preparation routes in this first slice.

## Out of scope

- functional invitation creation, acceptance, resend, revocation, or email delivery;
- user list, role editing, deactivation, password reset, or profile management;
- protection of every preparation API and route;
- refresh tokens, external identity providers, multi-factor authentication, or multi-tenancy.

## Acceptance criteria

- bootstrap is available only while no user exists and creates exactly one Administrator;
- duplicate bootstrap is rejected transactionally;
- invalid login returns a generic response and does not reveal account existence;
- successful login sets an HttpOnly SameSite cookie and `/auth/me` resolves the user;
- logout revokes the server session and clears the cookie;
- settings API returns 401 without a valid session and 403 for a non-Administrator;
- password values and raw session tokens never appear in normal API responses, database history, or logs;
- frontend bootstrap/login/settings guard works on desktop and mobile without horizontal overflow;
- Alembic has one head `h10014`;
- exact-head Quality, document, operator, guided acceptance, PostgreSQL, and Docker gates pass.
