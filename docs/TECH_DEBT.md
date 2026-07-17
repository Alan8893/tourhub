# TourHub Technical Debt

Status date: 2026-07-17

Implemented through merged PR #79:

- complete guided project preparation from creation through branded documents;
- persisted shopping, equipment, user overrides, recalculation, and reload-safe readiness;
- singleton club branding through Alembic `h10007`;
- general, document-specific, and guided desktop/mobile release gates;
- installation and first-start runbook;
- backup-first update and recovery runbook;
- host-side PostgreSQL custom-format backup and confirmed restore with a pre-restore safety dump;
- migration, health, LAN, volume, and rollback boundaries;
- focused Operator Docs validation.

Draft PR #80 addresses Docker runtime debt:

- immutable backend/frontend release images without application bind mounts;
- production frontend build served by Nginx;
- internal-only PostgreSQL and Redis networking;
- explicit health checks and same-origin API proxying;
- clean-environment build/start validation;
- persisted API data verification after application restart;
- Alembic current-head verification and focused Docker diagnostics.

Remaining priorities:

- PostgreSQL migration upgrade/downgrade smoke;
- final release workflow and checklist;
- active deployment catalogue data acceptance;
- catalogue-import interaction coverage.
