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

### System Settings, Access, and mail — PR #84 through PR #95

- typed settings owners and responsive `/settings` surface (`h10008`–`h10013`);
- Administrator bootstrap, sessions, invitations, users, roles, and preparation authorization (`h10014`–`h10016`);
- working SMTP delivery with manual invitation-link fallback;
- multiple sessions, immediate role propagation, deactivation revocation, protected-401 handling, exact route return, and visible current role.

### Recipe ownership foundation — TH-0086 / PR #96

- CLUB/PERSONAL scope and ownership-shape constraints (`h10017`);
- role-aware visibility and editing;
- one Backend policy for Recipe root, component, note, and equipment operations;
- Administrator-only permanent deletion with preserved Dish usage guards;
- responsive ownership UI and capability projection.

### Recipe publication and moderation — TH-0087 / PR #97

- lifecycle `draft`, `submitted`, `rejected`, and `published` (`h10018`);
- owner submission, rejection feedback, editing, and resubmission;
- submitted-recipe edit lock and row-locked transitions;
- Administrator/Verified Instructor moderation queue and self-review prevention;
- PERSONAL-to-CLUB publication with retained submitter attribution;
- responsive moderation UI and focused Chrome acceptance.

### Dish Recipe variants and generation modes — TH-0088 / PR #98

- ordered many-to-many Dish Recipe variants with one required published CLUB default;
- existing Dish defaults migrated to variant position zero through `h10019`;
- project modes `club_only`, `club_and_personal`, and `personal_preferred`;
- unrelated PERSONAL variants remain private;
- deterministic rotation through eligible variants while the CLUB default remains the shared fallback;
- selected Recipe persisted on MealSlotDish and compatibility MealPlanItem;
- manual assignments and manually edited slots preserve their stored Recipe;
- shopping and equipment use persisted assignment Recipes rather than the current Dish default;
- responsive Dish variant editor, project mode controls, and selected-Recipe presentation.

## NEXT

1. **Central alcohol prohibition** — one Backend policy across Product, Recipe, and CSV import paths, including existing-record handling.
2. **Actor-aware audit log** — safe real-actor history for project, menu, Recipe, moderation, settings, mail, user, and role changes.
3. **Consolidated export completeness** — approved complete Russian PDF and workbook contents using one immutable brand snapshot.
4. **Product acceptance and feature freeze** — catalogue/import acceptance, optional-scope decisions, and end-to-end scenarios.

## Deferred operations

- session administration, cleanup, global sign-out, and account recovery;
- asynchronous mail queues, scheduled retries, and delivery diagnostics beyond the current synchronous result;
- moderation notifications and immutable decision history before the actor-aware audit slice;
- per-meal manual Recipe switching and preference weights beyond the approved three project modes;
- additional same-origin request hardening if deployment expands beyond trusted LAN;
- external identity providers and MFA.

## Final release readiness

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- production-like deployment checklist;
- final release workflow and release tag after green exact-head gates.

Multi-tenant support and microservices remain prohibited.
