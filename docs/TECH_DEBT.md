# TourHub Technical Debt

Status date: 2026-07-17

## Implemented through merged PR #79

- complete guided project preparation from creation through branded documents;
- persisted shopping, equipment, user overrides, recalculation, and reload-safe readiness;
- singleton club branding through Alembic `h10007`;
- general, document-specific, and guided desktop/mobile release gates;
- installation and first-start runbook;
- backup-first update and recovery runbook;
- host-side PostgreSQL custom-format backup and confirmed restore with a pre-restore safety dump;
- migration, health, LAN, volume, and rollback boundaries;
- focused Operator Docs validation.

## Ready PR #80 — Docker runtime debt

- immutable backend/frontend release images without application bind mounts;
- production frontend build served by Nginx;
- internal-only PostgreSQL and Redis networking;
- explicit health checks and same-origin API proxying;
- clean-environment build/start validation;
- persisted API data verification after application restart;
- Alembic current-head verification and focused Docker diagnostics.

## Draft PR #81 — completeness and sequencing debt

- records the gap between the approved product specification and the current narrow single-user release path;
- moves final downgrade/re-upgrade migration smoke after first-release feature freeze;
- keeps basic Alembic, PostgreSQL, backup/restore, Docker, and full Quality gates mandatory during feature development;
- defines release-blocking and Product Owner decision items without changing runtime behavior.

## Release-blocking product debt

1. **Access foundation**
   - users, invitations, approved roles, authentication, sessions, guarded routes, and backend authorization.
2. **Recipe ownership and lifecycle**
   - CLUB/PERSONAL ownership, multiple variants, submission, review, approval, rejection comments, publication, and generation modes.
3. **Central alcohol prohibition**
   - one backend rule across Product, Recipe, and CSV import paths plus reviewed handling of existing prohibited records.
4. **Actor-aware audit log**
   - safe history for project, participant, menu, recipe, publication, user, and role changes.
5. **Consolidated export completeness**
   - approved complete Russian PDF and workbook sheets `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование` using one brand snapshot.
6. **Product acceptance**
   - active deployment catalogue data, catalogue-import interaction, and role-based end-to-end browser scenarios.

## Product Owner decisions required

- whether instructor preference-based generation priority blocks the first release;
- which recipe metadata fields are mandatory for the first release: preparation technology, tags, season compatibility, dietary restrictions, and richer categories;
- whether any approved access, moderation, audit, or export requirement is explicitly deferred from the first release.

## Deferred final release debt

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- final production-like deployment checklist;
- final release workflow and release tag.
