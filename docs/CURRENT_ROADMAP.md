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

### Access foundation — PR #90 through PR #93

- one-time Administrator bootstrap and server-owned sessions (`h10014`);
- functional invitation lifecycle and invited-user sign-in (`h10015`);
- user administration, explicit roles, activation state, and final-active-Administrator invariant (`h10016`);
- authenticated preparation routes and APIs for active Administrator, Instructor, and Verified Instructor users;
- public onboarding and invitation acceptance;
- Administrator-only settings, invitations, and user management.

### Working mail delivery — PR #94

- plain, STARTTLS, and implicit TLS SMTP;
- optional external authentication through `TOURHUB_SMTP_SECRET`;
- Administrator-only connection check and fixed Russian test message;
- best-effort invitation delivery after commit with manual-link fallback.

### Multi-user operational readiness — TH-0085 / PR #95

- multiple independent sessions and current persisted role resolution;
- complete session revocation on deactivation;
- centralized protected-401 handling and exact route return;
- visible current user role.

### Recipe ownership foundation — TH-0086 / PR #96

- Recipe scope is `club` or `personal`;
- database ownership-shape constraints and migration `h10017`;
- existing recipes remain CLUB; interactive creation produces owned PERSONAL recipes;
- role-aware visibility and editing for Administrator, Instructor, and Verified Instructor;
- Administrator-only permanent deletion with preserved Dish usage guards;
- one Backend policy protects root, component, note, and equipment operations;
- responsive frontend ownership labels and server-projected capabilities.

PR #96 implementation head `29b84be3f98a721d8d0faf2fa1908f65681820cd` passed Quality #858, Document Quality #474, Guided Release Acceptance #425, Operator Docs #411, and Docker Release Runtime #406.

## NEXT

1. **Recipe publication and moderation** — submission, review queue, publication, rejection with comment, resubmission, and lifecycle history.
2. **Dish recipe variants and generation modes** — multiple recipes per Dish and approved club/personal selection modes.
3. **Central alcohol prohibition** — one Backend policy across Product, Recipe, and CSV import paths.
4. **Actor-aware audit log** — safe real-actor history for project, menu, recipe, settings, mail, user, and role changes.
5. **Consolidated export completeness** — approved complete Russian PDF and workbook contents using one immutable brand snapshot.
6. **Product acceptance and feature freeze** — catalogue/import acceptance, optional-scope decisions, and end-to-end scenarios.

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
