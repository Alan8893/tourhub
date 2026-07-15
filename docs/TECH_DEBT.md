# TourHub Technical Debt

Status date: 2026-07-15

Technical debt is prioritized by product risk, not by implementation convenience.

## P0 — Release Blockers

No unresolved P0 item currently applies to the selected single-user release scope.

## P1 — Quality and Maintainability

### TD-005 — Ruff backlog

The audited snapshot contained 195 Ruff violations. A clean critical baseline and selected workflow baseline are enforced in CI; continue expanding module coverage without increasing debt.

### TD-006 — Strict mypy backlog

The audited snapshot contained 74 strict mypy errors. Selected workflow modules are clean and enforced in CI; continue fixing and adding modules incrementally.

### TD-007 — Frontend automated tests

Implemented coverage includes MealPlan states and mutations, recipe editor validation and lifecycle flows, dish catalogue validation, project catalogue rendering through production build, and catalogue-import template contracts.

Remaining critical coverage:

- project creation and guided preparation;
- shopping recalculation presentation;
- catalogue-import interaction and error rendering;
- responsive and higher-level interaction behavior;
- invitation and role administration when multi-user mode starts.

### TD-008 — Continuous Integration

Implemented gates include backend tests, selected Ruff and strict mypy baselines, Alembic single-head validation, frontend tests and production build, moderate dependency audit, and PostgreSQL 18 backup/restore smoke testing.

Remaining:

- Docker image/build validation;
- final release-acceptance workflow.

### TD-010 — Documentation and ADR consistency

Canonical current documents and the task index are synchronized as of 2026-07-15. Historical documents and duplicate ADR-011 history still require explicit archival or canonical labeling where ambiguity remains.

## P2 — Product Completion Debt

### TD-002 — Multi-user authorization baseline

Invitation-only registration, secure local authentication, role enforcement, recipe ownership, and administration are deferred until the single-user release workflow is complete. They remain part of the approved full product target and are mandatory before sensitive multi-user data is introduced.

### TD-011 — Recipe ownership and moderation

The single-club recipe library, safe archive, guarded deletion, and bulk import are complete. Remaining work covers CLUB/PERSONAL ownership, multiple recipe variants per Dish, publication review, and verified-instructor moderation.

### TD-012 — Menu diversity engine

Implement MealSlot-based composition rules, three-day main-dish diversity, same-day uniqueness, future preference modes, and warning fallback when the catalogue is insufficient.

### TD-013 — Equipment domain completion

Persist recipe equipment requirements, aggregate maximum simultaneous need, support manual overrides, and join equipment to the transactional recalculation chain.

### TD-014 — Export templates and branding

Complete Russian PDF/Excel templates and load club logo and name from system settings.

### TD-015 — Audit log

Record safe actor/action/time metadata when multi-user access and administration are introduced.

### TD-017 — Meal plan editor UX

Complete TH-0065: Russian labels, compact dish rows, domain meal order, responsive full-width editing, collapsible days, mutation feedback, and responsive tests.

### TD-019 — Dish recipe change impact preview

Before recipe replacement is confirmed, show how many existing meal plans, purchase lists, and checklists will be recalculated.

### TD-020 — Alcohol prohibition enforcement

Apply the approved prohibition consistently in backend product creation, recipe and dish workflows, and catalogue import, with regression tests.

## Completed History

- TD-001 — accidental and legacy public API placeholders removed; OpenAPI contract covered.
- TD-003 — participant-count changes, MealSlot mutations, and Dish recipe replacement refresh implemented purchase lists and checklists transactionally with rollback coverage. Future equipment recalculation is tracked by TD-013.
- TD-004 — complete local stack startup, migrations, and the primary workflow verified during stabilization; final acceptance remains under TD-008.
- TD-009 — current frontend lockfile passes the enforced moderate-severity dependency audit.
- TD-016 — backup and restore scripts, documentation, and PostgreSQL 18 CI smoke test implemented.
- TD-018 — dish catalogue, explicit active-recipe assignment, frontend editing, archived-recipe history, and purchasing recalculation implemented.
- Recipe library foundation — product, component, note, archive, restore, guarded deletion, and transactional CSV import implemented through API and frontend.

## Debt Closure Rule

A debt item is closed only when implementation, regression coverage, documentation, task status, and equivalent active-debt cleanup are complete.
