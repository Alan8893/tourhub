# TourHub Technical Debt

Status date: 2026-07-14

Technical debt is prioritized by product risk, not by implementation convenience.

## P0 — Release Blockers

### TD-002 — Authorization baseline

Implement invitation-only registration, role enforcement, and secure local authentication before sensitive club data is introduced.

### TD-003 — Recalculation consistency

Participant-count and MealSlot changes now recalculate persisted purchasing data transactionally. Complete the contract for dependent equipment after equipment persistence is implemented.

## P1 — Quality and Maintainability

### TD-005 — Ruff backlog

The audited snapshot contained 195 Ruff violations. A clean critical baseline and selected workflow baseline are enforced in CI; continue expanding module coverage without increasing debt.

### TD-006 — Strict mypy backlog

The audited snapshot contained 74 strict mypy errors. Selected workflow modules are clean and enforced in CI; continue fixing and adding modules incrementally.

### TD-007 — Frontend automated tests

Implemented coverage:

- MealPlan loading, error, empty, and ready states;
- MealSlot add, replace, remove, pending, validation, and mutation-error states.

Remaining critical coverage:

- project creation;
- shopping recalculation display;
- invitation and role administration;
- responsive and higher-level interaction behavior.

### TD-008 — Continuous Integration

Implemented GitHub Actions gates:

- backend tests;
- critical and selected Ruff baselines;
- selected strict mypy baseline;
- Alembic single-head validation;
- frontend tests;
- frontend TypeScript and production build;
- moderate-severity dependency audit;
- PostgreSQL 18 backup/restore smoke test.

Remaining:

- Docker image/build validation;
- final release-acceptance workflow.

### TD-010 — Documentation and ADR consistency

Current canonical product, status, roadmap, domain, and architecture documents are synchronized. Legacy documentation and duplicate ADR-011 history still require explicit archival/canonical labeling where ambiguity remains.

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

### TD-017 — Meal plan editor UX

Redesign the functional but cramped MealSlot editor before final MVP UI acceptance. The tracked task is `TH-0065`.

Required improvements:

- fully Russian labels and placeholders;
- compact dish rows with clear add, replace, and remove hierarchy;
- domain-order meal sorting instead of alphabetical sorting;
- responsive full-width editing layout;
- collapsible day sections and better visual scanning;
- per-mutation loading, success, and error feedback;
- frontend coverage for responsive states.

## Completed History

- TD-001 — Public API placeholders: accidental and legacy public placeholders removed; OpenAPI contract covered.
- TD-004 — Docker release verification baseline: complete local stack startup, migrations, and primary implemented flow verified during stabilization. Final acceptance remains under TD-008.
- TD-009 — Dependency vulnerability: current lockfile passes enforced moderate-severity `npm audit`.
- TD-016 — Backup and restore: Bash/PowerShell scripts, operational documentation, and PostgreSQL 18 CI smoke test implemented.

## Debt Closure Rule

A debt item is closed only when:

- implementation is merged;
- regression tests or executable checks exist;
- documentation is updated;
- the item is removed from the active register or moved to completed history;
- no equivalent untracked debt remains in active task documents.
