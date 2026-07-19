# TourHub Current Roadmap

Status date: 2026-07-19

## Product goal

Operate the approved local ERP release for one tourist club without changing the modular-monolith architecture or accepted single-club boundary.

```text
First-release preparation and operations
  → System Settings and Access
  → Recipe ownership, moderation, Dish variants, and generation modes
  → Actor-aware audit foundation
  → complete Russian exports and central alcohol prohibition
  → Product acceptance, release readiness, and v0.1.0
  → Project workspace UX (TH-0095)
  → Product catalogue editing (TH-0097)
  → Published Recipe Dish synchronization (TH-0098)
  → Project audit coverage (TH-0099)
  → Menu generation and MealSlot audit coverage (TH-0100)
```

## Released first-release sequence

- complete guided preparation from Project creation through Menu, shopping, checklist, equipment, readiness, and Russian documents;
- production-like local Docker runtime, backup/restore, health checks, LAN access, and restart persistence;
- typed System Settings, invitation-only Access, users, roles, SMTP delivery, and multi-session readiness;
- CLUB/PERSONAL Recipe ownership, moderation, ordered Dish variants, generation modes, and persisted assignment Recipe snapshots;
- append-only actor-aware AuditEvent foundation through `h10020`;
- complete consolidated Project exports;
- centralized no-exceptions alcohol policy and final Alembic head `h10021`;
- machine-readable Product Acceptance and Release Readiness evidence;
- immutable `v0.1.0` release tag and backup-based production rollback boundary.

## Delivered post-release improvements

### TH-0095 — Project workspace navigation

Compact routed Overview, Menu, Shopping, Equipment, and Documents work areas with responsive navigation and no horizontal overflow at accepted widths.

### TH-0097 — Product catalogue editing

Shared Product fields can be corrected without changing Product IDs, Recipe relationships, or RecipeComponent values.

### TH-0098 — Published Recipe Dish synchronization

Publication synchronizes the Recipe into Dishes in the publication transaction. Exact-name matches become variants; otherwise one role-less Dish is created. Generator roles remain explicitly human-owned.

### TH-0099 — Project audit coverage

Project creation, participant recalculation, generation-mode changes, and full preparation orchestration create semantic actor-attributed events in owning transactions with no-op suppression and rollback safety.

### TH-0100 — Menu generation and MealSlot audit coverage

- initial generation and regeneration record `meal_plan_generated` in the MealPlan/Equipment transaction;
- bounded snapshots record plan/day/slot/dish/manual-slot counts and warnings;
- regeneration records Recipe generation mode and preserved manual-slot context;
- manual add/remove/replace record semantic events inside the existing purchasing/checklist/equipment recalculation transaction;
- failures roll back domain changes and pending AuditEvents together;
- Administrator Audit UI/API expose Russian Menu and MealSlot labels and filters;
- candidate exact head passed strict Ruff/mypy, all 327 Backend tests, complete Frontend/browser acceptance, Product Acceptance, backup/restore, Alembic, Docker, documentation, guided-release, operator, and final-readiness gates;
- Alembic remains `h10021` and `v0.1.0` remains immutable.

## Next post-release selection

No task after TH-0100 is selected automatically. System Settings and mail-operation audit are the first listed unresolved audit slice, but work requires a separate Product Owner decision.

## Deferred non-blocking priorities

### Audit coverage

- System Settings and mail operations;
- invitation creation, revocation, acceptance, and delivery results;
- catalogue/import, shopping, equipment, and document-generation writes;
- audit export, retention UI, SIEM, undo, and replay.

### Product and operations

- account recovery, session administration, user profiles, asynchronous mail, bounce handling, and advanced templates;
- richer Recipe metadata, per-meal switching, and preference weights;
- Product/Dish archive-management UI and ownership-aware import UX;
- participant profiles, routes/GPX, warehouse, procurement, and external aggregation domains;
- scheduled/emailed documents, signatures, and encrypted configuration archives.

Multi-tenant support and microservices remain prohibited.
