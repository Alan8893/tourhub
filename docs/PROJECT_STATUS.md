# TourHub Project Status

Status date: 2026-07-21

## Current phase

TourHub v0.1.0 remains immutable at its released Alembic head `h10021`. The current post-release application head is `h10022`.

The feature-frozen first release is complete through TH-0093. Post-release work delivered routed Project UX (TH-0095), Product editing (TH-0097), published Recipe-to-Dish synchronization (TH-0098), audit coverage through TH-0103, and authenticated personal profiles plus club contacts through TH-0104.

## Verified baseline

- one current Alembic head ending at `h10022` and PostgreSQL 18 migration/runtime verification;
- immutable release tag `v0.1.0` at its recorded release SHA and released migration head `h10021`;
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness on pull requests and `main`;
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only;
- TH-0104 changes identity profile persistence and authenticated UX only; project, menu, calculation, document-format, and single-club boundaries are unchanged.

## Delivered post-release improvements

### Project workspace and catalogue workflow

- compact routed Project work areas and responsive navigation through TH-0095;
- shared Product editing without changing Product IDs, Recipe relationships, or RecipeComponent values through TH-0097;
- transaction-owned published Recipe-to-Dish synchronization with explicit human-owned generator readiness through TH-0098.

### Actor-aware audit

- append-only AuditEvent persistence and safe actor snapshots through `h10020`;
- semantic coverage for user access, Recipe moderation, Projects, Menu/MealSlot, settings/mail, invitations, catalogue/import, shopping, equipment, and documents through TH-0103;
- TH-0104 adds `account_profile_updated` with changed field names and versions only;
- TH-0104 adds `account_password_changed` with version and revoked-login counts only;
- phone numbers, social links, passwords, hashes, cookies, raw sessions, tokens, request bodies, and exception details are excluded.

### Personal account and club contacts

- `/account` is available to every authenticated active user;
- the header account control and sidebar item replace the former header logout button;
- one existing `display_name` field serves as FIO and login email remains read-only;
- optional phone, Telegram, MAX, and VK values accept handles or approved HTTPS links and persist normalized values;
- all authenticated active users may view active club contacts;
- email, `tel:` links, platform links, and downloadable vCard support day-to-day instructor contact work;
- password change verifies the current password, preserves the current login, and revokes every other active login;
- logout is available from the personal account page.

## TH-0104 evidence

Implementation candidate `9a1ab8f7eace70e25a3471a7f0abd690de45e2ab` passed strict Ruff/mypy, the full Backend test suite, Frontend tests/build/full browser acceptance, Product Acceptance, PostgreSQL backup/restore, Alembic single-head validation, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness.

The final documentation and Audit-label head is verified through the same exact-head workflow set before merge.

## Deferred non-blocking debt

- email/phone verification, account recovery, account deletion, avatars, public participant profiles, and general session administration UI;
- audit export, retention UI, external SIEM integration, operational diagnostics, undo, and event replay;
- ownership-aware import UX and Product/Dish archive-management UI;
- moderation notifications, asynchronous mail, and bounce handling;
- richer Recipe metadata, per-meal switching, and preference weights;
- routes/GPX, warehouse and procurement domains;
- scheduled/emailed documents, persisted versions, signatures, and encrypted configuration archives.

## Next work

TH-0104 is complete after exact-head verification. No later task is selected automatically. Further work requires another explicit Product Owner decision.
