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
- best-effort invitation delivery after commit with manual-link fallback;
- no migration; Alembic remained at `h10016`.

### Multi-user operational readiness — TH-0085 / PR #95

- multiple independent sessions and current persisted role resolution;
- complete session revocation on deactivation;
- centralized protected-401 handling and exact route return;
- visible current user role;
- no migration; Alembic remained at `h10016`.

PR #95 merged as `82315e0ff9520b52ae5244f69bc05d4a5d0db5b3`. Exact implementation head `8570670209566f6860b71c0173557bb71bf6fe00` passed Quality #843, Document Quality #460, Guided Release Acceptance #411, Operator Docs #397, and Docker Release Runtime #392.

## IN PROGRESS — TH-0086 / DRAFT PR #96

### Recipe ownership foundation

- Recipe scope is `club` or `personal`;
- `owner_user_id` is required for PERSONAL and prohibited for CLUB;
- migration `h10017` preserves existing recipes as CLUB;
- interactive creation produces a PERSONAL recipe owned by the current user;
- Administrator sees all recipes; other roles see CLUB plus owned PERSONAL recipes;
- Instructor edits owned PERSONAL recipes;
- Verified Instructor edits owned PERSONAL and CLUB recipes;
- Administrator edits all and remains the only permanent-delete role;
- root, component, note, and equipment endpoints share one Backend policy;
- frontend displays scope, owner, read-only state, and server-projected capabilities.

Scope boundary:

- no submission, publication, review queue, rejection comments, or moderation history;
- no PERSONAL-to-CLUB transition;
- no multiple Recipe variants per Dish;
- no personal-recipe generation modes;
- no actor-aware audit in this slice.

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
