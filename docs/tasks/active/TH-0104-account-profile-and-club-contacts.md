# TH-0104 — Account Profile and Club Contacts

## Status

IN PROGRESS

## Goal

Replace the header logout action with an authenticated personal account surface that lets every active club user maintain their own contact profile, view active club contacts, change their password safely, and sign out.

## Scope

- Reuse the existing `display_name` field as one full-name field.
- Keep email read-only because it remains the unique login identifier.
- Add optional phone, Telegram, MAX, and VK profile fields.
- Accept either a username or a full platform link and persist a normalized link.
- Expose active users' contact cards to every authenticated active user.
- Make phone numbers tappable through `tel:` and provide a downloadable vCard for saving a contact.
- Add `/account`, a clickable current-user control in the header, and a `Личный кабинет` navigation item.
- Move logout into the account page.
- Allow password change with current-password verification and a repeated new password.
- Keep the current session active and revoke all other sessions after password change.
- Audit profile changes using changed field names only and password changes without passwords or hashes.

## Privacy and validation

- Email cannot be changed in this task.
- Contact fields are visible to authenticated active users only.
- Empty contact values are stored as `NULL`.
- Phone accepts a human-friendly international representation and is normalized for `tel:`/vCard use.
- Social links are restricted to Telegram, MAX, and VK HTTPS hosts.
- Audit payloads do not contain phone numbers, social URLs, passwords, hashes, cookies, session tokens, or arbitrary request bodies.

## Non-goals

- Avatar upload.
- Public unauthenticated profiles.
- Email or phone verification.
- Account deletion or recovery.
- Separate first/middle/last-name columns.
- Session administration UI beyond revoking other sessions after password change.

## Acceptance

- Alembic introduces the optional profile columns with one new head.
- Backend tests cover normalization, authenticated visibility, profile ownership, vCard safety, password validation, session revocation, audit attribution, and rollback.
- Frontend tests and real-Chrome acceptance cover desktop/mobile layout, profile editing, contact actions, password change, header navigation, and logout.
- All release gates remain green and `v0.1.0` remains immutable.
