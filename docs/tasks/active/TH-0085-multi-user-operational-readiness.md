# TH-0085 — Multi-User Operational Readiness

Status: IN PROGRESS

Last updated: 2026-07-18

## Goal

Validate and harden the existing single-club multi-user foundation before introducing user-owned recipes or more detailed business permissions.

## Scope

### Backend

- verify that one user may hold multiple independent active server sessions;
- verify that role changes are resolved from the current persisted User on every authorized request;
- verify that deactivation revokes every active session for that user;
- preserve optimistic-version conflict handling and the final-active-Administrator invariant;
- add focused integration coverage without changing persistence or the approved role matrix.

### Frontend

- react centrally when a protected API request returns HTTP 401;
- clear stale local identity immediately and redirect through the existing route guards;
- preserve the complete requested destination, including query and hash, through sign-in;
- preserve the current destination after explicit logout;
- display the current user role next to the current user name;
- keep failed login responses local to the login form rather than treating them as an expired active session.

### Acceptance

- browser acceptance covers Administrator bootstrap, exact route return, visible role, explicit logout, server-side session revocation, and successful sign-in after revocation;
- Backend integration covers two simultaneous sessions for one Instructor, immediate role propagation, and revocation of both sessions after deactivation;
- existing Administrator-only and preparation-access boundaries remain unchanged;
- no migration is required and Alembic remains at `h10016`.

## Out of scope

- session list, individual session revocation, global sign-out, cleanup, or retention UI;
- password reset, account recovery, MFA, or external identity providers;
- per-project ownership, private projects, teams, ACLs, or row-level permissions;
- live collaborative editing, WebSocket synchronization, or conflict-free replicated state;
- recipe ownership and moderation, which remain the next product capability;
- multi-tenancy or multiple clubs in one installation.

## Definition of done

- all acceptance criteria are implemented and covered by focused tests;
- frontend build and browser acceptance pass;
- Backend tests and static checks pass;
- current status, roadmap, technical debt, and task index are synchronized;
- the exact PR head passes the repository quality gates.
