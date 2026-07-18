# TH-0082 — User Administration and Roles

Status: IN PROGRESS

Last updated: 2026-07-18

## Goal

Provide Administrator-owned user administration for one local TourHub club without introducing account deletion, password reset, or broad preparation authorization.

## Scope

### Backend

- add optimistic user versions through additive Alembic `h10016` while retaining one head;
- expose an Administrator-only user list with role, active state, timestamps, and current-user marker;
- allow Administrators to change Instructor, Verified Instructor, and Administrator roles;
- allow activation and deactivation of existing users;
- revoke all active sessions when a user is deactivated;
- prevent any operation that would leave the installation without an active Administrator;
- reject stale updates with HTTP 409 and return clear Russian errors;
- keep user deletion, password reset, and profile self-service unavailable.

### Frontend

- add a dedicated responsive `Пользователи` section under System Settings;
- show users, roles, activity state, and the current account;
- provide explicit save actions with confirmation for deactivation or Administrator demotion;
- handle stale-version conflicts and reload the authoritative Backend state;
- preserve desktop and mobile usability without horizontal overflow.

## Out of scope

- account deletion, password reset, email change, self-service profile editing, or bulk operations;
- invitation creation changes or automatic mail delivery;
- broad preparation-route/API authorization;
- consolidated actor-aware audit history;
- external identity providers, MFA, or multi-tenancy.

## Acceptance criteria

- only an authenticated Administrator can list or update users;
- the user list never returns password hashes or session tokens;
- role and activation changes require the current expected version;
- stale updates return HTTP 409;
- deactivation revokes active sessions immediately;
- the last active Administrator cannot be deactivated or demoted;
- an Administrator may manage other users and, when another active Administrator exists, their own role/state;
- responsive user administration works on desktop and mobile;
- Alembic has one head `h10016`;
- exact-head Quality, document, operator, guided acceptance, PostgreSQL, and Docker gates pass.
