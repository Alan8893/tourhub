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
  → Recipe ownership foundation
  → Recipe publication and moderation
  → Dish recipe variants and generation modes
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

### Access and mail foundation — PR #90 through PR #95

- one-time Administrator bootstrap and server-owned sessions (`h10014`);
- functional invitation lifecycle and invited-user sign-in (`h10015`);
- user administration, explicit roles, activation state, and final-active-Administrator invariant (`h10016`);
- authenticated preparation routes for all approved active roles;
- working SMTP delivery with manual invitation-link fallback;
- multiple independent sessions, current persisted role resolution, complete deactivation revocation, protected-401 handling, exact route return, and visible current role.

### Recipe ownership foundation — TH-0086 / PR #96

- Recipe scope is `club` or `personal`;
- database ownership-shape constraints and migration `h10017`;
- existing recipes remain CLUB; interactive creation produces owned PERSONAL recipes;
- role-aware visibility and editing for Administrator, Instructor, and Verified Instructor;
- Administrator-only permanent deletion with preserved Dish usage guards;
- one Backend policy protects root, component, note, and equipment operations;
- responsive frontend ownership labels and server-projected capabilities.

PR #96 merged as `d9ee573d44d885b48a2ce9424e9695f25d95a665`.

### Recipe publication and moderation — TH-0087 / PR #97

- lifecycle states `draft`, `submitted`, `rejected`, and `published`;
- migration `h10018` preserves existing CLUB recipes as published;
- owner submission, rejection feedback, editing, and resubmission;
- submitted-recipe root/component/note/equipment/archive lock;
- Administrator/Verified Instructor moderation queue;
- Verified Instructor self-review prevention;
- PERSONAL-to-CLUB publication with retained submitter attribution;
- rejection with a required comment and latest-decision metadata;
- row-locked lifecycle transitions;
- responsive lifecycle/moderation UI and focused Chrome acceptance driven by Backend capabilities.

Implementation head `7dd0ddd398b4f4b82d43f30db8c95c0489f2f31b` passed Quality #887, Document Quality #502, Guided Release Acceptance #453, Operator Docs #439, and Docker Release Runtime #434.

## NEXT

1. **Dish recipe variants and generation modes** — multiple recipes per Dish and approved club/personal selection modes.
2. **Central alcohol prohibition** — one Backend policy across Product, Recipe, and CSV import paths.
3. **Actor-aware audit log** — safe real-actor history for project, menu, recipe, moderation, settings, mail, user, and role changes.
4. **Consolidated export completeness** — approved complete Russian PDF and workbook contents using one immutable brand snapshot.
5. **Product acceptance and feature freeze** — catalogue/import acceptance, optional-scope decisions, and end-to-end scenarios.

## Deferred operations

- session administration, cleanup, global sign-out, and account recovery;
- asynchronous mail queues, scheduled retries, and delivery diagnostics beyond the current synchronous result;
- moderation notifications and immutable decision history before the actor-aware audit slice;
- additional same-origin request hardening if deployment expands beyond trusted LAN;
- external identity providers and MFA.

## Final release readiness

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- production-like deployment checklist;
- final release workflow and release tag after green exact-head gates.

Multi-tenant support and microservices remain prohibited.
