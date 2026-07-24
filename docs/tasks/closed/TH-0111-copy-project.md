# TH-0111 — Copy Project

Status: DONE

## Goal

Allow a Project owner or Administrator to create a new draft Project from a completed Project template without reopening or mutating the source and without copying historical or derived operational artifacts.

## Delivered product contract

- Copy is available only for a source Project with `status=completed`.
- The authenticated actor must be the source owner or an Administrator; additional instructors cannot copy it.
- The new Project uses editable ordinary creation parameters: name, participants, days, start date, first meal, last meal, and Recipe generation mode.
- The destination receives a new identity, `status=draft`, and the authenticated actor as owner.
- The completed source and its team remain unchanged.
- Repeating a request creates a separate destination; the UI disables submission while one request is pending.

## Copy matrix

### Copied

- the destination MealSlot schedule is recreated from the new parameters;
- source assignments are copied only into matching `(day_number, meal_type)` slots;
- Dish and selected Recipe identities are retained only when they remain active, visible, and permitted by the current Recipe-generation and alcohol-policy boundary;
- the selected Project Recipe generation mode is stored on the destination.

### Recreated or recalculated

- Project, MealPlan, day, slot, assignment, and compatibility item identities;
- participant-dependent quantities and derived preparation state through the ordinary later preparation workflow;
- shopping, checklist, equipment, readiness, and document projections only when explicitly generated for the new Project.

### Not copied

- source owner or additional instructors;
- completion state, timestamps, or audit history;
- shopping lists, purchase/checklist state, equipment lists, readiness state, generated documents, or delivery history;
- archived or policy-invalid catalogue assignments;
- notifications.

## Backend

- added `ProjectCopyRequest` and bounded `ProjectCopyResponse`;
- added `POST /api/v1/projects/{project_id}/copy`;
- added transactional `ProjectCopyService` using centralized Project visibility/ownership checks, `MealScheduleEngine`, catalogue activity, Recipe visibility, and current policy rules;
- missing/invalid assignments are skipped with bounded warnings while the source remains untouched;
- destination state and semantic `project_copied` audit commit or roll back together;
- no migration was required.

## Frontend

- eligible completed Projects expose `Копировать` from Project settings;
- the normal Project form is reused with source values as editable defaults;
- copy mode explains the exact copy boundary and blocks active/non-completed sources;
- duplicate submission is blocked while the mutation is pending;
- success navigates to the new draft Project and presents copied/skipped counts plus bounded warnings;
- responsive behavior is preserved.

## Verification

- Backend tests cover successful copy, matching-slot projection, source immutability, owner/Administrator authorization, additional-instructor rejection, completed-only policy, invalid dependency skips, semantic audit, and forced-audit rollback;
- Frontend unit tests cover editable defaults and copied/skipped result presentation;
- real-Chrome acceptance verifies edited request mapping, duplicate-submit guard, source immutability, destination navigation, warning presentation, and 360 px overflow;
- Quality validates Ruff, mypy, full Backend tests, Frontend tests/build/browser acceptance, PostgreSQL backup/restore, and one Alembic head;
- Product Acceptance, Docker Release Runtime, Document Quality, Guided Release Acceptance, Operator Docs, and Final Release Readiness remain required on the exact final head;
- Alembic remains one head at `h10023`;
- immutable `v0.1.0` remains unchanged.

## Non-goals retained

- copying an active/draft Project;
- selecting another destination owner or pre-populating the source team;
- bulk templates or scheduled recurring Projects;
- copying derived purchasing/equipment/document state;
- notification delivery;
- event replay or undo.
