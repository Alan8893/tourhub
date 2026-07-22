# ADR-026 — Project Ownership and Team-Scoped Access

- Status: Accepted
- Date: 2026-07-22

## Context

TourHub supports multiple authenticated Administrators, Instructors, and Verified Instructors inside one club, but Projects previously had no persisted owner or collaboration list. Every preparation-capable user could list and address every Project through direct API paths. TH-0104 also exposed all active-user contacts from the personal account, while the approved workflow now requires contacts to be shared only inside a Project team.

The Product Owner approved these rules:

- the user who creates a Project becomes its owner;
- Administrators may view every Project;
- owners may add multiple active users as additional Project instructors, including Administrators participating in a trip;
- additional instructors may view Menu and operate Shopping, Checklist, Equipment, Documents, and Project contacts, but may not change Menu, Project settings, team, ownership, status, or deletion;
- owners and Administrators may transfer ownership, and the previous owner remains an additional instructor;
- completed Projects remain readable but cannot be changed or reopened;
- inactive team members retain historical membership while losing runtime access;
- global User roles must remain singular;
- future email, Telegram, and MAX notifications must not be implemented yet;
- copying a completed Project is a separate future capability.

## Decision

### Project-scoped responsibilities

Keep the existing singular global User role and add two Project-scoped responsibilities:

- `owner`, persisted as `Project.owner_user_id`;
- `additional_instructor`, persisted by `ProjectInstructor(project_id, user_id)`.

An Administrator may therefore have global administrative authority and also appear explicitly in a Project team without introducing global multi-role persistence.

### Central access policy

`ProjectAccessPolicy` is the authoritative Backend boundary. It derives capabilities from the current persisted User, Project owner/team membership, active state, global Administrator role, and Project completion state.

The policy is applied to Project reads and every Project-scoped preparation route. Unrelated users receive HTTP 404 so Project existence and membership are not disclosed. Authenticated team members receive HTTP 403 for forbidden role-specific actions. Writes to a completed Project receive HTTP 409.

Frontend capabilities are presentation guidance only. Backend checks remain authoritative.

### Capability matrix

- Administrators: view every Project; manage Project/team/Menu while open; operate shopping/equipment/documents; transfer ownership; complete/delete.
- Owner: same Project-level capabilities as an Administrator for the owned Project.
- Additional instructor: view Project and Menu; operate shopping/checklist/equipment/documents while open; no Menu, settings, team, ownership, completion, or deletion writes.
- Completed Project: readable and downloadable only; owner/Administrator may still delete it.

### Ownership transfer

Ownership transfer is one transaction:

1. validate and lock Project/current/new owners;
2. remove the new owner from additional-instructor membership when present;
3. add the previous owner as an additional instructor when absent;
4. update `owner_user_id`;
5. append `project_owner_transferred`;
6. commit or roll back the entire change.

### Existing-Project migration

Alembic `h10023` adds the ownership/team schema. Existing Projects are backfilled from the earliest trustworthy `project_created` AuditEvent whose actor still exists. If unavailable, the first Administrator by ID is used. An inactive creator remains the owner; active Administrators can later transfer ownership. The migration does not create AuditEvents.

### Contacts

Remove club-wide contact listing from `/account`. Project team responses expose the owner and additional instructors only after Project visibility is established. vCard download is also Project-scoped. Inactive historical members remain visible to Project managers but contact actions are unavailable.

### Completion

`completed` is terminal in the current model. Completed Projects are hidden by default in the catalogue and are read-only. No reopen endpoint is provided.

`Копировать проект` is explicitly deferred: a later task may create a new Project from a completed template without reopening or mutating the source.

### Notifications

Define `ProjectTeamNotificationService` with a no-op implementation for instructor add/remove and ownership transfer. No queue, delivery record, provider integration, or message is created in this task.

### Audit

Append bounded semantic events in the owning transaction:

- `project_instructor_added`;
- `project_instructor_removed`;
- `project_owner_transferred`;
- `project_status_updated`;
- `project_deleted`.

Payloads may contain Project/User IDs, display names, global/project roles, and state changes. Phone numbers, social URLs, credentials, tokens, arbitrary request bodies, and notification-provider details are excluded.

## Consequences

### Positive

- Project confidentiality is enforced consistently at Backend boundaries.
- Collaboration supports any number of instructors without changing global identity semantics.
- Administrator participation as a trip instructor is represented explicitly.
- Contact exposure follows the Project access boundary.
- Completed Projects provide immutable operational history and a stable source for future copying.
- Future notification channels have an explicit integration seam.

### Costs

- Every Project-scoped route must resolve Project membership before work.
- Existing fixtures and integrations must provide or migrate a Project owner.
- Capability projection and browser acceptance become part of the Project API contract.
- Copy semantics still require a separate Product Owner decision.

## Rejected alternatives

- Global multi-role User persistence: rejected because Project participation is contextual and a global redesign would affect invitations, administration, session projection, and invariants.
- Frontend-only filtering: rejected because direct API URLs would bypass it.
- Automatic ORM-wide access/audit hooks: rejected in favor of explicit semantic policy and transaction boundaries.
- Reopening completed Projects: rejected; copying will create a new identity in a future task.
- Club-wide contact directory in the personal account: rejected because contacts belong to collaboration context.
