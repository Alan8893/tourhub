# TH-0105 — Project Ownership, Team Access and Project Contacts

## Status

DONE

## Goal

Restrict each Project to Administrators, its creator-owner, and explicitly added active instructors; give collaborators approved operational access without Menu/settings control; move contact cards from the personal account into the Project context; and make completed Projects terminal read-only history.

## Delivered scope

### Identity and persistence

- Existing singular global roles remain unchanged.
- `Project.owner_user_id` stores the creator-owner.
- `ProjectInstructor` stores any number of additional instructors, including explicitly participating Administrators.
- Alembic `h10023` backfills existing owners from the earliest trustworthy `project_created` AuditEvent, with first-Administrator fallback.
- Inactive owners/members retain historical relationships while losing runtime access.

### Access policy

`ProjectAccessPolicy` protects Project catalogue/detail, Menu/MealSlot, preparation, Shopping/PurchaseList, Checklist, Equipment, Documents, team contacts, settings, completion, ownership transfer, and deletion.

- Administrator: sees every Project and has owner-equivalent management while open.
- Owner: manages Project, Menu, preparation, team, ownership, completion, deletion, and all modules.
- Additional instructor: views Project/Menu; operates Shopping, Checklist, Equipment, Documents, and contacts while open; cannot write Menu or Project/team settings.
- Outsider: receives no catalogue item and HTTP 404 on direct/nested routes.
- Completed Project: terminal read-only history; owner/Administrator may delete it.

### Team lifecycle

- Owner/Administrator may atomically replace multiple additional instructors.
- Candidates include active Instructors, Verified Instructors, and Administrators grouped in the UI.
- Removed users lose direct access immediately.
- Ownership transfer may select any active supported user.
- The new owner is removed from additional membership.
- The previous owner remains an additional instructor.
- No-op updates create no AuditEvent.

### Contacts and account

- Club-wide contact cards and `/account/contacts` are removed.
- `/account` retains personal profile editing, password change, and logout.
- Project overview shows owner plus explicit additional instructors only.
- Active Project team contacts provide mail, `tel:`, Telegram, MAX, VK, and Project-scoped vCard.
- Inactive historical members are identified without contact actions.

### Completion and catalogue

- `completed` is terminal and has no reopen endpoint.
- Completed Projects are hidden by default behind `Показывать завершённые`.
- Frontend modules become read-only according to Backend capabilities.
- Documents remain available to authorized users as historical output.

### Audit and notifications

- Added `project_instructor_added`.
- Added `project_instructor_removed`.
- Added `project_owner_transferred`.
- Added `project_status_updated`.
- Added `project_deleted`.
- Events exclude phone numbers, social URLs, credentials, tokens, request bodies, and provider details.
- `ProjectTeamNotificationService` exists with a no-op implementation; no email, Telegram, or MAX message is sent.

### Future Product context

`Копировать проект` is explicitly recorded in `CURRENT_ROADMAP.md` and `TECH_DEBT.md`. It will be a separate task that creates a new Project identity from a completed template and must define the exact copy matrix before implementation.

## Acceptance evidence

- focused Backend tests cover catalogue/direct visibility, capability matrix, multiple instructors, immediate removal, transfer, completion, deletion, deactivation/reactivation, project-scoped vCard, audit attribution, and rollback;
- migration acceptance covers creator recovery, Administrator fallback, and downgrade;
- Frontend build/tests cover capability-aware surfaces;
- dedicated real-Chrome acceptance covers completed filtering, collaborator read-only Menu, Project contacts, vCard, and 360 px overflow;
- account browser acceptance verifies that club-wide contacts are gone;
- strict Ruff and mypy pass;
- full Backend regression and Alembic single-head validation pass;
- PostgreSQL backup/restore and clean Docker release runtime pass;
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness pass on the implementation candidate;
- immutable `v0.1.0` remains unchanged at released head `h10021`.

## Architecture

ADR-026 records the Project-scoped role, policy, migration, contact, completion, audit, and future-copy boundaries.
