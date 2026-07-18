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

Mail boundary:

- `MailSettings` owns only non-secret host, port, connection mode, optional username, sender metadata, test recipient, timeout, retry count, and optimistic version;
- the deployment-managed SMTP value remains in `TOURHUB_SMTP_SECRET` and is not accepted or returned by application APIs;
- `MailDeliveryService` owns plain, STARTTLS, and implicit-TLS connection behavior, fixed message construction, bounded synchronous retries, and safe results;
- no-auth SMTP is allowed when no username is configured;
- invitation persistence commits before automatic delivery is attempted;
- delivery failure never invalidates the new invitation or removes the one-time manual link;
- queues, background workers, provider APIs, arbitrary templates, attachments, bounce processing, and delivery history remain separate future capabilities.

`main` and PR #94 use Alembic head `h10016`; PR #94 has no migration.

MealSlot and MealSlotDish remain primary. MealPlanItem remains compatibility-only.

Multi-tenancy and microservices remain prohibited.

See `PRODUCT_SPEC.md` and ADR-012 through ADR-019.
