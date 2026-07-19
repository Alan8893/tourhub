# TH-0094 — Project and Menu Audit Instrumentation

Status: IN PROGRESS

Started: 2026-07-19

Release baseline: `v0.1.0`

Alembic head: `h10021`

## Goal

Extend the existing actor-aware append-only AuditEvent foundation to the highest-priority documented post-release gap: Project and Menu mutations. Record semantic, safe, transaction-owned events without changing the released product workflow, schema, authorization matrix, or frontend business rules.

## Approved source

`PRODUCT_SPEC.md` requires audit history for Project changes, participant-count changes, and menu editing. ADR-023 and current technical debt explicitly defer these owning-domain instrumentation slices after the shared AuditEvent foundation. TH-0094 implements that already-approved coverage; it does not introduce a new product capability.

## Scope

### Project events

- Project creation;
- Project parameter changes that affect preparation, including name, participant count, duration, dates/meal boundaries, Recipe generation mode, and status where supported by the existing API;
- one semantic event per successful mutation;
- bounded before/after snapshots containing only Project-owned fields;
- actor snapshot from the authenticated current User;
- event and Project mutation commit or roll back together.

### Menu events

- initial menu generation and later regeneration;
- manual MealSlot Dish add, replace, and remove operations supported by the existing API;
- semantic context identifying Project, MealPlan/day/slot, Dish, and persisted Recipe assignment where applicable;
- no re-derivation of historical Recipe selection from a mutable Dish default;
- event and menu mutation commit or roll back together.

### Query and UI compatibility

- existing Administrator-only audit API remains the read boundary;
- existing generic Audit UI must display the new events without adding a product-specific parallel history store;
- action/entity filters remain compatible;
- no secret, cookie, session, token, request-body, or arbitrary object logging.

### Verification

- focused service/API tests for each event family;
- actor snapshot, action, entity type/ID, before/after/context assertions;
- transaction rollback test proving no AuditEvent survives a failed mutation;
- existing Project/menu behavior and authorization remain green;
- existing Audit immutability and secret filtering remain green;
- no migration and Alembic head remains `h10021`.

## Out of scope

- System Settings, mail, invitation, catalogue/import, shopping, equipment, and document-generation audit events;
- audit export, retention UI, SIEM, undo, event replay, automatic ORM-wide auditing, or realtime notifications;
- new Project ownership/ACL rules;
- new menu editing capability or Recipe-selection behavior;
- frontend-owned authorization or business validation;
- schema changes unless a reproducible defect proves the existing AuditEvent model insufficient;
- any modification to tag `v0.1.0` or its released baseline.

## Design rules

- reuse `AuditService.record` and ADR-023 sanitization;
- action names remain bounded snake_case semantic identifiers;
- entity IDs identify the owning business record, while related IDs belong in safe context;
- snapshots contain explicit whitelisted fields rather than serialized ORM objects;
- the owning service controls transaction order and performs one commit;
- do not add an automatic SQLAlchemy interceptor;
- preserve exact selected Recipe IDs already stored on MealSlotDish.

## Definition of done

- [ ] Project creation and update events are implemented and verified.
- [ ] Participant-count changes are distinguishable in Project before/after snapshots.
- [ ] Menu generation/regeneration events are implemented and verified.
- [ ] Manual MealSlot Dish add/replace/remove events are implemented and verified.
- [ ] AuditEvent and business mutations share one transaction and rollback behavior.
- [ ] Existing Audit API/UI can query and present the new events.
- [ ] Existing Project/menu/access/audit tests remain green.
- [ ] Ruff, strict mypy scope, Backend tests, Frontend build/tests, Product Acceptance, and release workflows remain green.
- [ ] Alembic head remains `h10021`.
- [ ] Current architecture/domain/status/roadmap/technical-debt documentation is synchronized.
- [ ] Scope and review threads are clean before squash-merge.
