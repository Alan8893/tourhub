# TourHub Technical Debt

Status date: 2026-07-16

Technical debt is prioritized by product risk.

## P0 — Release blockers

No open P0 release blockers are recorded after TH-0070 / PR #54.

## P1 — Quality and maintainability

### TD-005 — Ruff backlog

The audited snapshot contained 195 Ruff violations. Critical and selected workflow baselines are enforced. Continue expanding coverage without increasing debt.

### TD-006 — Strict mypy backlog

The audited snapshot contained 74 strict mypy errors. Selected workflow modules, including meal policy, role-aware generator, MealPlanService mapping, and catalogue readiness, are clean and enforced.

### TD-007 — Frontend and browser automated tests

Current coverage includes pure state, command, validation, ordering, summary, feedback, readiness presentation, quantity parsing, and responsive-policy helpers.

Real-browser coverage includes:

- MealSlot add, replace, and remove operations;
- explicit removal confirmation;
- Russian success and injected mutation-error feedback;
- Dish role and meal-type classification through React Query and Axios;
- exact atomic classification payload;
- readiness warning refresh after role mutation;
- responsive mobile navigation;
- desktop, tablet, and 360 px no-overflow checks;
- stable screenshot artifacts.

Merged PR #64, #66, #67, and #69 add backend integration coverage for role-aware generation, calendar-day diversity, manual-slot regeneration, and warning persistence.

Draft PR #70 adds:

- frontend pure tests for purchased-quantity parsing, formatting, progress, and responsive layout;
- real-browser checklist loading through React Query and Axios;
- purchased-quantity PATCH verification;
- remaining-quantity refresh after mutation;
- checked-state PATCH and progress verification;
- 360 px no-overflow coverage and screenshot output.

Remaining critical coverage:

- complete guided project preparation;
- active deployment catalogue acceptance data;
- package-count and package-surplus presentation;
- catalogue import interaction and error rendering;
- final end-to-end release acceptance.

### TD-008 — Continuous Integration

Implemented gates include backend tests, selected Ruff/mypy, Alembic single-head, frontend tests/build/audit, browser acceptance suites, and PostgreSQL backup/restore.

Remaining:

- explicit migration upgrade/downgrade smoke against PostgreSQL;
- Docker image/build validation;
- final release-acceptance workflow.

### TD-010 — Documentation and ADR consistency

Canonical status, roadmap, context, domain, architecture, and active menu task are synchronized through merged PR #65, #66, #67, and #69. Draft PR #70 advances the status, roadmap, technical debt, and TH-0061 task into shopping review. ADR-013 remains the accepted source for persisted role and meal-type ownership. ADR-006 is superseded where it described MealPlanItem as primary.

Historical archive documents and duplicate ADR-011 history still require explicit canonical labelling where ambiguity remains.

### TD-024 — Legacy MealPlanItem compatibility

MealSlot is primary. MealPlanItem remains persisted for compatibility and increases mapping and recalculation complexity.

PR #67 rebuilds compatibility MealPlanItem rows while regenerating the same persisted MealPlan, including authoritative manual-slot dishes.

Required later:

- identify remaining consumers;
- verify legacy-only recalculation behavior;
- create a migration/removal plan;
- remove duplicate persistence only through an approved compatibility change.

## P2 — Product completion debt

### TD-002 — Multi-user authorization baseline

Invitation-only registration, secure local authentication, roles, recipe ownership, and administration are deferred until the single-user workflow is accepted.

### TD-011 — Recipe ownership and moderation

Remaining work covers CLUB/PERSONAL ownership, multiple recipe variants, publication review, and verified-instructor moderation.

### TD-012 — Meal composition and diversity

Implemented through merged PR #59, #60, #61, #64, #65, #66, #67, and #69:

- normalized Dish-owned role and meal-type compatibility;
- roles `main`, `addition`, `drink`, and `snack`;
- repeatability per `(dish, role)`;
- deterministic catalogue readiness;
- role- and meal-type-aware production generation;
- stable composition persistence order;
- explicit required-pool warnings without incompatible fallback;
- archived and unclassified automatic exclusion;
- same-day uniqueness and calendar-day three-day `main` diversity;
- day-four reuse and repeatable-main bypass;
- Alembic revision `h10002` and authoritative manual slots;
- preservation of non-empty and empty manual slots across regeneration;
- one project MealPlan reused during regeneration;
- Alembic revision `h10003` and persisted warning snapshot;
- identical warnings on later GET responses;
- atomic warning replacement and clearing;
- pure, service, persistence, mutation, migration, and public API coverage.

Remaining work is operational or requirement-dependent:

- maintain explicit classification of the active deployment catalogue;
- define larger candidate thresholds and preference modes only after approved requirements.

### TD-013 — Equipment domain completion

Persist recipe equipment requirements, aggregate maximum simultaneous need, support manual overrides, and join equipment to transactional recalculation.

### TD-014 — Export templates and branding

Complete Russian PDF/Excel templates and load club logo and name from settings.

### TD-015 — Audit log

Record actor/action/time metadata when multi-user access is introduced.

### TD-019 — Dish recipe change impact preview

Show how many existing plans and purchasing projections will be recalculated before recipe replacement.

### TD-020 — Alcohol prohibition enforcement

Apply the prohibition consistently in backend product, recipe, dish, and import validation with regression tests.

### TD-025 — Complete Product CRUD

Product currently supports list and create. Update and guarded delete remain unimplemented.

### TD-026 — Shopping and packaging review

The calculation and persistence foundations exist, but the complete user review is not finished.

Draft PR #70 delivers:

- project checklist product names;
- required, purchased, and non-negative remaining quantities;
- negative purchased-quantity validation;
- editable checked state and purchased quantities;
- progress and responsive feedback presentation.

Required after PR #70:

- present calculated package count and package surplus/remainder clearly;
- add optional responsible-person text;
- integrate shopping review into the complete guided preparation acceptance flow;
- verify recalculation changes remain visible without losing user purchase progress.

## Completed history

- TD-001 — accidental public API placeholders removed.
- TD-003 — participant, MealSlot, and Dish recipe purchasing refresh implemented transactionally.
- TD-004 — local stack and primary workflow verified during stabilization.
- TD-009 — dependency audit passes at moderate severity.
- TD-016 — backup/restore scripts and CI smoke test implemented.
- TD-017 — Meal Plan Editor UX and responsive browser acceptance completed by TH-0065 / PR #57.
- TD-018 — dish catalogue and active-recipe assignment implemented.
- TD-021 — MealSlot relation identifiers and `/dishes` frontend contract repaired by PR #54.
- TD-022 — invalid selection-count pseudo cooldown removed by PR #54.
- TD-023 — backend meal-boundary authority and regression tests delivered by PR #54.
