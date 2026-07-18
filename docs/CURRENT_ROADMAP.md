# TourHub Current Roadmap

Status date: 2026-07-18

## Product goal

Deliver the approved local MVP for one tourist club without changing the approved modular-monolith architecture.

```text
Project preparation baseline
  → Production-like Docker runtime
  → Product completeness audit
  → System Settings foundation
  → Access foundation
  → Working mail delivery
  → Multi-user operational readiness
  → Recipe ownership and lifecycle
  → Central alcohol prohibition
  → Actor-aware audit
  → Consolidated Russian exports
  → Product acceptance and feature freeze
  → Final migration and release gates
```

## DONE

### Infrastructure, preparation, and operations

- complete guided preparation from project creation through shopping, equipment, readiness, and Russian PDF/Excel/print/ZIP outputs;
- installation, update, backup, restore, recovery, production-like release images, health checks, same-origin API proxy, restart persistence, and cleanup validation;
- PostgreSQL 18 and Redis remain internal to the release network.

### System Settings foundation — PR #84 through PR #89

- typed club, appearance, document, module, invitation-policy, and mail-metadata owners;
- responsive `/settings` surface;
- optimistic versions, PostgreSQL row locks, HTTP 409 conflicts, and safe focused history;
- migrations `h10008` through `h10013`.

### Access foundation — PR #90 through PR #93

- one-time Administrator bootstrap and server-owned sessions (`h10014`);
- functional invitation lifecycle and invited-user sign-in (`h10015`);
- user administration, explicit roles, activation state, and final-active-Administrator invariant (`h10016`);
- authenticated preparation routes and APIs for active Administrator, Instructor, and Verified Instructor users;
- public onboarding and invitation acceptance;
- Administrator-only settings, invitations, and user management.

PR #90 merged as `26c4d4eb9246de44579451fe3d6e7bd631538324`. PR #91 merged as `2348870864efa1da20547c1a6564dc5f9b6488ef`. PR #92 merged as `257d82a9f4f7e47095f8e96635bf62a9ed14e722`. PR #93 merged as `21a66a2caae4e52f8e1a87bd242666703c4bc296`.

### Working mail delivery — PR #94

- Python standard-library SMTP client with plain, STARTTLS, and implicit TLS modes;
- optional SMTP authentication using the deployment-managed `TOURHUB_SMTP_SECRET` value only when a username is configured;
- Administrator-only connection check and fixed Russian test message;
- configured timeout and bounded synchronous retries;
- invitation create/reissue attempts automatic delivery after the invitation transaction commits;
- delivery failure never rolls back a valid invitation and the manual one-time link always remains available;
- safe status messages, responsive UI, fake-SMTP tests, and Chrome acceptance;
- no migration; Alembic remains at `h10016`.

PR #94 merged as `3c51d4c1d0bb0bd96d23a1f4ace0947ae48e9101`.

### Multi-user operational readiness — TH-0085 / PR #95

- focused Backend integration for two independent sessions belonging to one user;
- current persisted role is resolved on every request and becomes visible to both sessions immediately;
- user deactivation revokes every active session for that user;
- protected frontend HTTP 401 responses clear stale identity centrally;
- exact path, query, and hash are preserved through re-authentication;
- explicit logout preserves the current destination;
- the current role is visible in the application header;
- browser acceptance covers bootstrap, route return, logout/login, server-side revocation, and recovery;
- no migration; Alembic remains at `h10016`.

Implementation head `4879e6dc701550935eb4d173e5098de85d264fd5` passed Quality #835, Document Quality #452, Guided Release Acceptance #403, Operator Docs #389, and Docker Release Runtime #384.

## NEXT

1. **Recipe ownership and lifecycle** — CLUB/PERSONAL ownership, variants, submission, review, publication, rejection, archive, and Verified Instructor distinctions.
2. **Central alcohol prohibition** — one Backend policy across Product, Recipe, and CSV import paths.
3. **Actor-aware audit log** — safe real-actor history for project, menu, recipe, settings, mail, user, and role changes.
4. **Consolidated export completeness** — approved complete Russian PDF and workbook contents using one immutable brand snapshot.
5. **Product acceptance and feature freeze** — catalogue/import acceptance, optional-scope decisions, and end-to-end scenarios.

## Deferred operations

- session administration, cleanup, global sign-out, and account recovery;
- asynchronous mail queues, scheduled retries, and delivery diagnostics beyond the current synchronous result;
- additional same-origin request hardening if deployment expands beyond trusted LAN;
- external identity providers and MFA.

## Final release readiness

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- production-like deployment checklist;
- final release workflow and release tag after green exact-head gates.

Multi-tenant support and microservices remain prohibited.
