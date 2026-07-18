# TourHub Current Architecture

Status: Active

Last updated: 2026-07-18

TourHub is a single-club modular monolith with PostgreSQL in production.

Current architecture decisions:

- System Settings use independent typed owners under one responsive surface: ADR-014.
- Accounts, roles, invitations, and user administration follow ADR-015 through ADR-017.
- Preparation access follows ADR-018.
- Working mail delivery follows ADR-019.
- Active Administrator, Instructor, and Verified Instructor users may use preparation workflows.
- Settings, invitation management, user management, connection checks, and test-message actions remain Administrator-only.
- Module visibility is presentation only and never grants access.
- Frontend route guidance never replaces Backend permission checks.

Access runtime:

- one User may own multiple independent server sessions;
- PostgreSQL stores only session-token hashes and session metadata;
- Backend resolves the current persisted User on every authorized request, so role and active-state changes are not cached in the browser token;
- deactivation revokes every active session for the affected User in the same transaction;
- the common frontend API client treats a protected HTTP 401 as session invalidation and clears stale local identity through AuthProvider;
- failed authentication entry requests remain local form errors and do not represent revocation of an active session;
- route guards preserve the exact path, query, and hash through sign-in;
- the application header exposes the current display name and role;
- session-list administration, individual revocation, global sign-out, account recovery, project ownership, and row-level ACLs remain separate future capabilities.

Mail boundary:

- `MailSettings` owns only non-secret host, port, connection mode, optional username, sender metadata, test recipient, timeout, retry count, and optimistic version;
- the deployment-managed SMTP value remains in `TOURHUB_SMTP_SECRET` and is not accepted or returned by application APIs;
- `MailDeliveryService` owns plain, STARTTLS, and implicit-TLS connection behavior, fixed message construction, bounded synchronous retries, and safe results;
- no-auth SMTP is allowed when no username is configured;
- invitation persistence commits before automatic delivery is attempted;
- delivery failure never invalidates the new invitation or removes the one-time manual link;
- queues, background workers, provider APIs, arbitrary templates, attachments, bounce processing, and delivery history remain separate future capabilities.

`main` uses Alembic head `h10016`. TH-0085 has no migration.

MealSlot and MealSlotDish remain primary. MealPlanItem remains compatibility-only.

Multi-tenancy and microservices remain prohibited.

See `PRODUCT_SPEC.md` and ADR-012 through ADR-019.
