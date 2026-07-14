# TourHub Technical Debt

Status date: 2026-07-14

Technical debt is prioritized by product risk, not by implementation convenience.

## P0 — Release Blockers

### TD-001 — Public API placeholders

Remove, implement, or explicitly deprecate public endpoints that raise `NotImplementedError` or expose unfinished contracts.

### TD-002 — Authorization baseline

Implement invitation-only registration, role enforcement, and secure local authentication before sensitive club data is introduced.

### TD-003 — Recalculation consistency

Guarantee that participant-count and meal composition changes recalculate ingredients, packages, shopping, and dependent equipment without changing selected dishes.

### TD-004 — Docker release verification

Verify the full local stack with `docker compose up --build`, database migrations, frontend, backend, and OpenAPI.

## P1 — Quality and Maintainability

### TD-005 — Ruff backlog

The audited snapshot contained 195 Ruff violations. Establish a clean baseline and enforce it in CI.

### TD-006 — Strict mypy backlog

The audited snapshot contained 74 strict mypy errors. Fix incrementally by module and enforce the agreed baseline in CI.

### TD-007 — Frontend automated tests

Add tests for critical flows:

- project creation;
- meal generation display;
- MealSlot editing;
- shopping recalculation display;
- invitation and role administration.

### TD-008 — Continuous Integration

Add GitHub Actions gates for:

- backend tests;
- Ruff;
- mypy;
- Alembic single-head validation;
- frontend type-check and build;
- frontend tests;
- dependency audit;
- Docker build.

### TD-009 — Dependency vulnerability

Update Vite and related dependencies to remove the high-severity issue reported by `npm audit`, without changing the approved stack.

### TD-010 — Documentation and ADR consistency

Resolve contradictory MealSlot documentation, duplicate ADR-011 files, obsolete task states, and stale API/module descriptions.

## P2 — Product Completion Debt

### TD-011 — Recipe ownership and moderation

Implement CLUB, PERSONAL, and ARCHIVED recipe scopes, publication review, verified-instructor moderation, and safe archival.

### TD-012 — Menu diversity engine

Implement the approved three-day main-dish diversity rule, same-day uniqueness, preference modes, and warning fallback.

### TD-013 — Equipment domain completion

Connect recipe equipment requirements to aggregated trip equipment with manual overrides.

### TD-014 — Export templates and branding

Complete Russian PDF/Excel templates and load club logo and name from system settings.

### TD-015 — Audit log

Record safe actor/action/time metadata for projects, menus, recipes, publication, invitations, roles, and administration.

### TD-016 — Backup and restore

Provide tested PostgreSQL backup and restore scripts and local operations documentation.

## Debt Closure Rule

A debt item is closed only when:

- implementation is merged;
- regression tests or executable checks exist;
- documentation is updated;
- the item is removed from this register or moved to a completed-history section;
- no equivalent untracked debt remains in active task documents.
