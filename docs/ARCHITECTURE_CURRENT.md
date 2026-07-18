# TourHub Current Architecture

Status: Active

Last updated: 2026-07-18

TourHub is a single-club modular monolith with PostgreSQL in production.

Current architecture decisions:

- System Settings use independent typed owners under one responsive surface: ADR-014.
- Accounts, roles, invitations, and user administration follow ADR-015 through ADR-017.
- Preparation access follows ADR-018.
- Active Administrator, Instructor, and Verified Instructor users may use preparation workflows.
- Settings, invitation management, and user management remain Administrator-only.
- Module visibility is presentation only and never grants access.
- Frontend route guidance never replaces Backend permission checks.
- `main` and PR #93 use Alembic head `h10016`; PR #93 has no migration.

MealSlot and MealSlotDish remain primary. MealPlanItem remains compatibility-only.

Multi-tenancy and microservices remain prohibited.

See `PRODUCT_SPEC.md` and ADR-012 through ADR-018.