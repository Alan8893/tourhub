# TH-0105 — Project Ownership, Team Access and Project Contacts

## Status

IN PROGRESS

## Goal

Introduce project-scoped ownership and instructor collaboration so each Project is visible only to active Administrators, its active owner, and its active additional instructors, while preserving read-only menu access for collaborators and moving contact cards from the personal account into the Project overview.

## Approved scope

- Every newly created Project stores the creating active user as its owner.
- Administrator, Instructor, and Verified Instructor users may create Projects.
- A Project may have any number of additional active instructors.
- Additional instructors may include Administrators when they participate in a trip as instructors.
- Active Administrators can view every Project even when they are not part of its team.
- Non-members cannot list or open the Project, including through direct project-scoped API URLs.
- Additional instructors may view the menu and operate shopping, checklist, equipment, contacts, and documents, but cannot create, regenerate, or manually edit menu assignments.
- Only the owner and Administrators may change Project parameters/settings, manage the team, transfer ownership, complete/delete the Project, or run full preparation.
- Ownership transfer keeps the previous owner as an additional instructor and removes the new owner from the additional-instructor set.
- Completed Projects are read-only and hidden by default behind a `Показывать завершённые` filter.
- Project overview exposes owner/additional-instructor contact cards with mail, phone, Telegram, MAX, VK, and vCard actions.
- The personal account keeps profile editing, password change, and logout, but no longer lists all club contacts.
- Existing Projects recover their owner from the earliest trustworthy `project_created` AuditEvent; when unavailable, the first Administrator is used as the migration fallback.
- Inactive owners/team members remain historical members but immediately lose access; reactivation restores access.
- Team writes and ownership transfer append bounded semantic AuditEvents in the owning transaction.
- A no-op notification boundary is introduced for future email, Telegram, and MAX delivery without sending anything in this task.

## Project roles

The global User role remains singular. `owner` and `additional_instructor` are Project-scoped responsibilities, allowing an Administrator to participate as an instructor without changing the global authorization model.

## Non-goals

- Global multi-role User persistence.
- Project-copy implementation.
- Email, Telegram, or MAX notifications.
- Participant profiles or public project/member pages.
- Reopening a completed Project.

## Future roadmap requirement

A later task will implement `Копировать проект`: create a new Project from a completed Project template, present the normal new-project parameter form, and copy menu plus approved preparation/settings data without reusing the old Project identity or dates.

## Acceptance

- One new Alembic head introduces owner/team persistence and deterministic existing-Project backfill.
- Central Backend project-access capabilities protect Project, Menu/MealSlot, preparation, shopping/checklist, equipment, documents, team contacts, settings, status, and deletion paths.
- Backend tests cover Administrator/owner/additional/outsider visibility, direct-link masking, completed read-only behavior, ownership transfer, inactive/reactivated users, migration fallback, audit attribution, and rollback.
- Frontend and real-Chrome acceptance cover team management, read-only collaborator menu, Project contacts, hidden completed Projects, personal-account cleanup, and 360 px layout.
- `Копировать проект` is present in the roadmap as deferred future work.
- All release gates remain green and immutable `v0.1.0` remains unchanged.
