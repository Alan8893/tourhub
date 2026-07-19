# TH-0099 — Project Audit Coverage

Status: IN PROGRESS

Started: 2026-07-19

## Goal

Add semantic actor-attributed audit events to Project creation, updates, and preparation while preserving existing behavior.

## Scope

- `project_created` shares the Project creation commit;
- `project_participants_updated` shares the participant recalculation transaction;
- `project_generation_mode_updated` shares the Project update commit;
- `project_prepared` shares the full preparation transaction;
- no-op updates create no event;
- failed operations leave neither domain changes nor audit events;
- the existing Administrator Audit API/UI exposes the events.

## Out of scope

- menu and MealSlot audit;
- audit expansion for settings, mail, invitations, import, shopping, equipment, or documents outside the preparation orchestration event;
- ORM-wide audit, undo, replay, export, retention, or external integrations;
- migrations, architecture changes, new Project capabilities, or release-tag movement.

## Definition of done

- four Project actions create actor-attributed events with bounded snapshots;
- preparation services support one caller-owned transaction without changing standalone behavior;
- service/API tests cover success, no-op, attribution, and rollback;
- all repository workflows pass on one exact final head;
- current documentation and task state are synchronized before squash merge.
