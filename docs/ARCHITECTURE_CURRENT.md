# TourHub Current Architecture

Status: Active

Last updated: 2026-07-18

TourHub is a single-club modular monolith with PostgreSQL in production.

## Current decisions

- System Settings use independent typed owners under one responsive surface: ADR-014.
- Accounts, roles, invitations, and user administration follow ADR-015 through ADR-017.
- Preparation access follows ADR-018.
- Working mail delivery follows ADR-019.
- Recipe ownership follows ADR-020.
- Active Administrator, Instructor, and Verified Instructor users may use preparation workflows.
- Settings, invitation management, user management, connection checks, and test-message actions remain Administrator-only.
- Module visibility is presentation only and never grants access.
- Frontend route guidance and capability projection never replace Backend permission checks.

## Access runtime

- one User may own multiple independent server sessions;
- PostgreSQL stores only session-token hashes and session metadata;
- Backend resolves the current persisted User on every authorized request, so role and active-state changes are not cached in the browser token;
- deactivation revokes every active session for the affected User in the same transaction;
- the common frontend API client treats a protected HTTP 401 as session invalidation and clears stale local identity through AuthProvider;
- failed authentication entry requests remain local form errors and do not represent revocation of an active session;
- route guards preserve the exact path, query, and hash through sign-in;
- explicit logout preserves the current destination for the next sign-in;
- the application header exposes the current display name and role;
- session-list administration, individual revocation, global sign-out, account recovery, project ownership, and row-level ACLs remain separate future capabilities.

## Recipe ownership boundary

- Recipe owns `scope`, nullable owner identity, archive state, components, notes, and equipment requirements;
- the database permits only CLUB without an owner or PERSONAL with an owner;
- existing shared catalogue rows migrate to CLUB;
- interactive creation produces PERSONAL recipes owned by the current actor;
- ownership-aware query services filter unrelated personal recipes before API projection;
- one centralized Recipe access policy is used by root, component, note, and equipment services;
- Administrator may manage all recipes, Verified Instructor may manage CLUB plus owned PERSONAL recipes, and Instructor may manage owned PERSONAL recipes only;
- permanent deletion remains Administrator-only and keeps existing usage guards;
- API capability fields guide Frontend controls, while Backend services remain authoritative;
- submission, publication, moderation, Dish variants, and generation modes remain later recipe lifecycle slices.

## Mail boundary

- `MailSettings` owns only non-secret host, port, connection mode, optional username, sender metadata, test recipient, timeout, retry count, and optimistic version;
- the deployment-managed SMTP value remains in `TOURHUB_SMTP_SECRET` and is not accepted or returned by application APIs;
- `MailDeliveryService` owns plain, STARTTLS, and implicit-TLS connection behavior, fixed message construction, bounded synchronous retries, and safe results;
- no-auth SMTP is allowed when no username is configured;
- invitation persistence commits before automatic delivery is attempted;
- delivery failure never invalidates the new invitation or removes the one-time manual link;
- queues, background workers, provider APIs, arbitrary templates, attachments, bounce processing, and delivery history remain separate future capabilities.

The current Alembic head is `h10017`.

MealSlot and MealSlotDish remain primary. MealPlanItem remains compatibility-only.

Multi-tenancy and microservices remain prohibited.

See `PRODUCT_SPEC.md` and ADR-012 through ADR-020.
