# TourHub Project Status

Status date: 2026-07-19

## Current phase

TourHub v0.1.0 is release-ready at Alembic head `h10021`.

The feature-frozen first release is complete through TH-0093. Post-release work delivered routed Project UX (TH-0095), Product editing (TH-0097), published Recipe-to-Dish synchronization (TH-0098), Project audit coverage (TH-0099), and menu/MealSlot audit coverage (TH-0100).

## Verified baseline

- PostgreSQL 18 migration cycle and one Alembic head ending at `h10021`;
- immutable release tag `v0.1.0` at its recorded release SHA;
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness on pull requests and `main`;
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only;
- no TH-0100 migration, architecture, runtime, generator, or calculation change.

## Delivered post-release improvements

### Project workspace and catalogue workflow

- compact routed Project work areas and responsive navigation through TH-0095;
- shared Product editing without changing Product IDs, Recipe relationships, or RecipeComponent values through TH-0097;
- transaction-owned published Recipe-to-Dish synchronization with explicit human-owned generator readiness through TH-0098.

### Actor-aware audit

- append-only AuditEvent persistence and safe actor snapshots through `h10020`;
- user-access and Recipe moderation actions in owning transactions;
- Project creation, participant recalculation, generation-mode updates, and preparation orchestration through TH-0099;
- initial generation and regeneration record `meal_plan_generated` with bounded plan counts, warnings, generation mode, and preserved manual-slot context through TH-0100;
- manual add/remove/replace record `meal_slot_dish_added`, `meal_slot_dish_removed`, and `meal_slot_dish_replaced` inside the existing purchasing/checklist/equipment recalculation transaction;
- failed generation, mutation, derived refresh, or audit recording rolls back domain changes and pending AuditEvents together;
- Administrator Audit UI/API expose Russian User, Recipe, Project, Menu, and MealSlot labels and filters.

## TH-0100 evidence

Candidate head `2f72de7eb0caaba358527d49cbd1b274f4b81f91` passed strict Ruff/mypy, all 327 Backend tests, Frontend tests/build/complete browser acceptance, Product Acceptance, PostgreSQL backup/restore, Alembic single-head validation, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness.

The final documentation-only head is verified again before merge.

## Deferred non-blocking debt

- semantic audit coverage for System Settings, mail, invitations, catalogue/import, shopping, equipment, and document-generation writes;
- audit export, retention UI, SIEM, undo, and replay;
- ownership-aware import UX and Product/Dish archive-management UI;
- moderation notifications, account recovery, session administration, asynchronous mail, and bounce handling;
- richer Recipe metadata, per-meal switching, and preference weights;
- participant profiles, routes/GPX, warehouse and procurement domains;
- scheduled/emailed documents, signatures, and encrypted configuration archives.

## Next work

TH-0100 is complete. No later task is selected automatically. System Settings and mail-operation audit remain the first listed unresolved audit slice and require another explicit Product Owner decision.
