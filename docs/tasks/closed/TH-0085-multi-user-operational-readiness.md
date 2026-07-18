# TH-0085 — Multi-User Operational Readiness

Status: DONE

Completed: 2026-07-18

Pull request: #95

## Goal

Validate and harden the existing single-club multi-user foundation before introducing user-owned recipes or more detailed business permissions.

## Delivered

### Backend

- focused integration proves that one User may hold multiple independent active server sessions;
- role changes are resolved from the current persisted User and become visible to every session on the next request;
- deactivation revokes every active session for the affected User;
- optimistic-version conflicts and the final-active-Administrator invariant remain unchanged;
- no persistence change or migration was required.

### Frontend

- the common API client emits one shared session-invalidated event when a protected request returns HTTP 401;
- AuthProvider clears stale local identity immediately and existing route guards redirect to sign-in;
- failed login responses remain local form errors rather than expired-session events;
- path, query, and hash are preserved through sign-in and explicit logout;
- the common header displays the current user name and role;
- role labels are shared between the header and user administration.

### Acceptance and documentation

- Chrome acceptance covers bootstrap, exact destination return, visible role, explicit logout, server-side session revocation, and successful recovery;
- current architecture, domain, project context, status, roadmap, technical debt, task index, and root README are synchronized with the multi-user baseline;
- TH-0084 mail delivery is moved to closed after merged PR #94;
- Alembic remains at `h10016`.

## Preserved boundaries

- no session-management UI, individual session revocation, global sign-out, cleanup, or account recovery;
- no per-project ownership, private projects, teams, ACLs, or row-level permissions;
- no live collaborative editing, WebSockets, or conflict-free replicated state;
- recipe ownership and moderation remain the next product capability;
- multi-tenancy remains prohibited.

## Verification

Implementation head `4879e6dc701550935eb4d173e5098de85d264fd5` passed:

- Quality #835;
- Document Quality #452;
- Guided Release Acceptance #403;
- Operator Docs #389;
- Docker Release Runtime #384.
