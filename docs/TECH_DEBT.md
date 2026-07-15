# TourHub Technical Debt

Status date: 2026-07-15

Technical debt is prioritized by product risk, not by implementation convenience.

## P0 — Release Blockers

### TD-003 — Recalculation consistency

Participant-count, MealSlot, and Dish recipe changes now recalculate persisted purchasing data transactionally. Complete the contract for dependent equipment after equipment persistence is implemented.

## P1 — Quality and Maintainability

### TD-005 — Ruff backlog

The audited snapshot contained 195 Ruff violations. A clean critical baseline and selected workflow baseline are enforced in CI; continue expanding module coverage without increasing debt.

### TD-006 — Strict mypy backlog

The audited snapshot contained 74 strict mypy errors. Selected workflow modules are clean and enforced in CI; continue fixing and adding modules incrementally.

### TD-007 — Frontend automated tests

Implemented coverage includes MealPlan states and mutations, recipe editor validation and lifecycle flows, dish catalogue validation, project catalogue rendering through production build, and catalog-import template contracts.

Remaining critical coverage:

- project creation and guided preparation;
- shopping recalculation presentation;
- catalog-import interaction and error rendering;
- responsive and higher-level interaction behavior;
- invitation and role administration when multi-user mode starts.

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

Canonical product, status, roadmap, domain, architecture, technical-debt, and task documents are synchronized as of 2026-07-15. Legacy documentation and duplicate ADR-011 history still require explicit archival/canonical labeling where ambiguity remains.

## P2 — Product Completion Debt

### TD-002 — Multi-user authorization baseline

Invitation-only registration, secure local authentication, role enforcement, recipe ownership, and administration are deliberately deferred until the single-user MVP workflow is complete. They remain mandatory before sensitive multi-user club data is introduced.

### TD-011 — Recipe ownership and moderation

The single-club recipe library, safe archive, guarded deletion, and bulk import are complete. Remaining work is limited to future CLUB/PERSONAL ownership scopes, multiple recipe variants per Dish, publication review, and verified-instructor moderation.

### TD-012 — Menu diversity engine

Implement meal composition rules, the approved three-day main-dish diversity rule, same-day uniqueness, future recipe preference modes, and warning fallback when the catalogue is insufficient.

### TD-013 — Equipment domain completion

Connect recipe equipment requirements to aggregated trip equipment with manual overrides and transactional recalculation.

### TD-014 — Export templates and branding

Complete Russian PDF/Excel templates and load club logo and name from system settings.

### TD-015 — Audit log

Record safe actor/action/time metadata when multi-user access and administration are introduced.

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

### TD-019 — Dish recipe change impact preview

Dish recipe replacement now recalculates all affected purchasing projections transactionally. Before final UX acceptance, show how many existing meal plans, purchase lists, and checklists will be recalculated before the user confirms the change.

### TD-020 — Alcohol prohibition enforcement

The approved product specification prohibits alcohol across product creation, recipes, dishes, and imports. Add centralized backend classification/validation and regression tests; frontend-only filtering is insufficient.

## Completed History

- TD-001 — Public API placeholders: accidental and legacy public placeholders removed; OpenAPI contract covered.
- TD-004 — Docker release verification baseline: complete local stack startup, migrations, and primary implemented flow verified during stabilization. Final acceptance remains under TD-008.
- TD-009 — Dependency vulnerability: current lockfile passes enforced moderate-severity `npm audit`.
- TD-016 — Backup and restore: Bash/PowerShell scripts, operational documentation, and PostgreSQL 18 CI smoke test implemented.
- TD-018 — Dish and recipe selection workflow: dish catalogue, explicit active-recipe assignment, frontend editing, historical archived-recipe visibility, and transactional purchasing recalculation are implemented.
- Recipe library foundation — product, component, note, archive, restore, guarded-delete, and transactional CSV-import workflows implemented through API and frontend.

## Debt Closure Rule

A debt item is closed only when:

- implementation is merged;
- regression tests or executable checks exist;
- documentation is updated;
- the item is removed from the active register or moved to completed history;
- no equivalent untracked debt remains in active task documents.