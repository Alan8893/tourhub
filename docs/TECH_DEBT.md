# TourHub Technical Debt

Status date: 2026-07-17

Implemented through merged PR #78:

- complete guided project preparation from creation through branded documents;
- persisted shopping, equipment, user overrides, recalculation, and reload-safe readiness;
- singleton club branding through Alembic `h10007`;
- general, document-specific, and guided desktop/mobile release gates.

Draft PR #79 addresses operator documentation debt:

- installation and first-start runbook;
- backup-first update and recovery runbook;
- host-side PostgreSQL custom-format backup script;
- confirmed restore with a pre-restore safety dump;
- migration, health, LAN, volume, and rollback boundaries;
- focused validation for scripts, links, required commands, and Docker Compose syntax.

Remaining priorities:

- Docker image build and runtime smoke;
- PostgreSQL migration upgrade/downgrade smoke;
- final release workflow and checklist;
- active deployment catalogue data acceptance;
- catalogue-import interaction coverage.
