# TH-0107 — Session Administration and Individual Revocation

Status: DONE

## Goal

Allow every active authenticated user to review their own active server sessions and revoke one other session without exposing session secrets or weakening the existing cookie-based authentication boundary.

## Delivered scope

- added an authenticated Backend projection of the current user's active non-expired sessions;
- identified the current session server-side from the existing HttpOnly session cookie;
- exposed only session ID, creation time, last-seen time, expiry time, and current-session marker;
- allowed the user to revoke one owned non-current active session by session ID;
- centralized session ownership, active-state checks, current-session protection, and revocation policy in `SessionAdministrationService`;
- recorded one safe semantic `account_session_revoked` AuditEvent in the same transaction as revocation;
- added a responsive session-management section to `/account` with loading, empty, success, progress, and failure states;
- added Backend, Frontend helper, and real-Chrome acceptance;
- retained one Alembic head `h10023` and preserved immutable tag `v0.1.0`.

## Backend policy

- all session-management routes require an active authenticated user;
- a user may list and revoke only sessions whose `user_id` matches the current User;
- unrelated, revoked, expired, and unknown session IDs are not disclosed and return 404;
- the current session cannot be revoked through the individual-revocation endpoint and returns 409; ordinary logout remains its termination path;
- token hashes and raw cookies never leave Backend persistence or appear in responses, logs, errors, audit payloads, or Frontend state;
- revocation locks the target row, marks `revoked_at`, appends a bounded AuditEvent, and commits or rolls back as one unit;
- audit context uses the sanitizer-safe flag `current_login_preserved` and contains no session/token/cookie fields;
- list reads do not mutate sessions beyond the existing centralized current-request `last_seen_at` update.

## Non-goals

- Administrator access to another user's sessions;
- global sign-out or a `revoke all` action;
- revoking the current session from the session list;
- IP address, browser, device, location, user-agent, or fingerprint collection;
- background cleanup or physical deletion of expired/revoked sessions;
- account recovery, password-reset flows, verified email/phone changes, account deletion, or retention policy;
- audit retention UI, Product/Dish archive management, ownership-aware CSV import UX, or Project copy;
- multi-tenant support, microservices, or changes to release tag `v0.1.0`.

## Verified acceptance

### Backend

- an authenticated user receives only their active non-expired sessions;
- exactly one returned row is marked current when the request cookie belongs to an active session;
- token hashes and raw tokens are absent from schemas and serialized responses;
- revoking another owned session makes that cookie fail immediately on the next protected request;
- unrelated, revoked, expired, and unknown sessions return 404 without revealing ownership;
- revoking the current session returns 409 and leaves it valid;
- revocation and `account_session_revoked` audit append share one transaction;
- forced audit failure rolls back `revoked_at`;
- audit payload contains bounded session ID/state metadata and `current_login_preserved` only, excluding tokens, hashes, cookies, IP/device data, and authorization headers.

### Frontend

- `/account` shows the current session and any other active sessions;
- current session is visibly labelled and has no individual revoke action;
- another session has a clear `Завершить` action with progress and error feedback;
- successful revocation removes the session from the list without logging out the current browser;
- the section remains usable without horizontal overflow at accepted mobile width.

### Real Chrome

- an authenticated user opens `/account` with two active sessions;
- the current session is labelled;
- the user revokes the other session;
- the browser sends the expected session ID to Backend;
- the revoked row disappears while the current account remains authenticated;
- the mobile account layout has no horizontal overflow.

## Migration

No migration was required because `auth_sessions` already stores ownership, token hash, creation, last-seen, expiry, and revocation timestamps. Current Alembic head remains `h10023`.
