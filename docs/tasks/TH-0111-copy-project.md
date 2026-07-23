# TH-0111 — Copy Project

Status: IN PROGRESS

## Goal

Allow a Project owner or Administrator to create a new draft Project from a completed Project template without reopening or mutating the source and without copying historical/derived operational artifacts.

## Product contract

- Copy is available only for a source Project with `status=completed`.
- The authenticated actor must be the source owner or an Administrator; additional instructors cannot copy it.
- The new Project uses the normal creation parameters supplied by the user: name, participants, days, start date, first meal, last meal, and Recipe generation mode.
- The new Project receives a new identity, `status=draft`, and the authenticated actor as owner.
- The completed source Project remains byte-for-byte unchanged by the operation.
- The source team is not copied; additional instructors must be assigned separately.

## Copy matrix

### Copied

- destination MealSlot schedule generated from the new Project parameters;
- source menu assignments for matching `(day_number, meal_type)` slots within the destination schedule;
- assigned Dish, meal role, selected Recipe identity, and immutable assignment snapshot only when the dependency remains usable under current catalogue and alcohol policy;
- Project-level Recipe generation mode through the normal creation request.

### Recreated or recalculated

- destination Project and MealSlot identities;
- participant-dependent quantities and derived preparation state;
- shopping/purchase/checklist/equipment projections after the normal preparation workflow is run.

### Not copied

- source owner/team membership;
- completion status;
- shopping lists, purchase state, checklist state, equipment lists, readiness state, generated documents, audit events, delivery history, or timestamps;
- archived or policy-blocked catalogue dependencies;
- notifications.

## Safety and transaction rules

- Source eligibility and authorization are rechecked inside the copy transaction.
- A source slot with an archived/policy-blocked Dish or unusable Recipe is left unassigned in the destination and reported as a bounded warning; the source is never changed.
- Destination creation, copied assignments, and semantic audit commit or roll back together.
- Audit action is `project_copied`; it records actor, source Project ID, destination Project ID, and bounded copied/skipped counts, but no full menu snapshots.
- Repeating the request creates a distinct new Project; the endpoint is intentionally non-idempotent and the UI must prevent accidental double submission.

## Backend

- add copy request/result DTOs around the normal Project creation fields;
- add a dedicated transactional Project copy service;
- add `POST /api/v1/projects/{project_id}/copy`;
- preserve existing Project create/list/get/update contracts;
- reuse central Project access, MealSchedule, catalogue activity, and alcohol-policy rules;
- add API/service tests for authorization, completed-only source, source immutability, matching-slot copy, dependency skips, recalculation boundary, audit, and rollback.

## Frontend

- add `Копировать проект` only on eligible completed Projects for owner/Administrator capabilities;
- reuse the normal Project parameter form with source values as editable defaults;
- show a clear copy matrix summary before submission;
- prevent duplicate submission and navigate to the new draft Project after success;
- show bounded skipped-assignment warnings and preserve responsive/mobile layout.

## Verification

- Backend unit/API coverage for success and all safety failures;
- Frontend unit coverage for eligibility, request mapping, duplicate-submit guard, and warning presentation;
- real-Chrome acceptance for completed-source copy, editable destination parameters, source immutability, success navigation, and mobile overflow;
- exact-head Quality, Product Acceptance, Docker Release Runtime, Document Quality, Guided Release Acceptance, Operator Docs, and Final Release Readiness must be green;
- Alembic must remain one head; add a migration only if persistence changes are unavoidable;
- immutable `v0.1.0` tag remains unchanged.

## Non-goals

- copying an active/draft Project;
- copying to another owner or pre-populating the source team;
- bulk Project templates or scheduled recurring Projects;
- copying derived purchasing/equipment/document state;
- notification delivery;
- event replay or undo.
