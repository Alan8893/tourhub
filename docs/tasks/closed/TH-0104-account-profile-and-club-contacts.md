# TH-0104 — Account Profile and Club Contacts

## Status

DONE

## Goal

Replace the header logout action with an authenticated personal account surface that lets every active club user maintain their own contact profile, view active club contacts, change their password safely, and sign out.

## Delivered scope

- Reused the existing `display_name` field as one FIO field.
- Kept email read-only because it remains the unique login identifier.
- Added optional phone, Telegram, MAX, and VK profile fields through Alembic `h10022`.
- Accepted either a handle or a full approved platform link and persisted canonical HTTPS links.
- Exposed active users' contact cards to every authenticated active user.
- Added `mailto:`, `tel:`, platform links, and downloadable vCard contact files.
- Added `/account`, a responsive current-user control in the header, and a `Личный кабинет` sidebar item.
- Removed the global header logout button and moved logout into the account page.
- Added password change with current-password verification and repeated new password.
- Preserved the current login and revoked every other active login after password change.
- Added `account_profile_updated` and `account_password_changed` semantic audit actions.
- Added Russian Administrator Audit labels for both account actions.

## Transaction and privacy rules

- Profile update locks the current User, checks optimistic `version`, and suppresses no-op saves.
- Profile mutation and AuditEvent commit or roll back together.
- Password hash change, other-login revocation, and AuditEvent commit or roll back together.
- Contact fields are visible to authenticated active users only; inactive users are excluded.
- Empty contact values are stored as `NULL`.
- Phone accepts a human-friendly representation and is normalized for `tel:`/vCard use.
- Social links are restricted to Telegram, MAX, and VK HTTPS hosts.
- Audit payloads contain versions, changed field names, current-login preservation, and revoked-login count only.
- Phone numbers, social URLs, passwords, hashes, cookies, raw session values, tokens, and arbitrary request bodies are excluded.

## Verification

Implementation candidate `9a1ab8f7eace70e25a3471a7f0abd690de45e2ab` passed:

- strict Ruff and mypy;
- the full Backend test suite;
- Alembic single-head validation at `h10022`;
- Frontend tests and production build;
- full browser acceptance, including the real `/account` page at mobile width;
- critical Product Acceptance Backend and Chrome scenarios;
- PostgreSQL backup/restore;
- Docker Release Runtime with the migrated `h10022` database;
- Document Quality, Guided Release Acceptance, Operator Docs, and Final Release Readiness.

The final documentation/Audit-label head is verified through the same exact-head workflow set before merge.

## Release boundary

- Current post-release Alembic head is `h10022`.
- Immutable tag `v0.1.0` remains at its recorded release commit and released head `h10021`.
- Final Release Readiness verifies the first-release migration cycle by checking out `v0.1.0`; Quality and Docker validate current head.

## Non-goals retained

- Avatar upload.
- Public unauthenticated profiles.
- Email or phone verification.
- Account deletion or recovery.
- Separate first/middle/last-name columns.
- General session-administration UI beyond revoking other logins after password change.
