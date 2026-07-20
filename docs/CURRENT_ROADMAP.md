# TourHub Current Roadmap

Status date: 2026-07-20

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
  → System Settings and mail audit coverage (TH-0101)
  → Invitation lifecycle and delivery-result audit coverage (TH-0102)
  → Catalogue/import, shopping, equipment, and document audit coverage (TH-0103)
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

Initial generation/regeneration and manual MealSlot Dish add/remove/replace record bounded semantic events in the owning recalculation transaction. Administrator UI/API expose Russian Menu and MealSlot labels.

### TH-0101 — System Settings and mail audit coverage

All typed settings owners and Administrator SMTP connection/test operations record safe actor-attributed events. Credentials, transcripts, exceptions, and request bodies are excluded.

### TH-0102 — Invitation lifecycle and delivery-result audit coverage

Invitation create/reissue/revoke/accept record in lifecycle transactions. Safe post-commit delivery outcomes preserve invitation validity and the manual link even when delivery or delivery-audit fails.

### TH-0103 — Operational write audit coverage

- Product create/update and successful Product/Recipe CSV apply record semantic events;
- catalogue import payloads contain aggregate counts only, never CSV content or row details;
- PurchaseList/PurchaseChecklist generation and manual responsible/progress updates record in their owning transaction;
- Recipe equipment requirements, EquipmentList generation, and manual equipment overrides/removals record bounded before/after state;
- preparation subservices called with `commit=False` append events to the caller-owned Project preparation transaction;
- no-op writes create no event and audit failure rolls back pending domain mutations;
- successful Project and legacy purchase-list document generation records kind/format/content type/size before response delivery without storing content or filenames;
- Administrator Audit UI/API expose Russian catalogue, shopping, equipment, and document labels and filters without mobile overflow;
- Alembic remains `h10021` and `v0.1.0` remains immutable.

## Next post-release selection

No task after TH-0103 is selected automatically. Further work requires a separate Product Owner decision.

## Deferred non-blocking priorities

### Audit and operations

- audit export, retention UI, external SIEM integration, and operational diagnostics;
- undo and event replay remain outside v0.1.0.

### Product and operations

- account recovery, session administration, user profiles, asynchronous mail, bounce handling, and advanced templates;
- richer Recipe metadata, per-meal switching, and preference weights;
- Product/Dish archive-management UI and ownership-aware import UX;
- participant profiles, routes/GPX, warehouse, procurement, and external aggregation domains;
- scheduled/emailed documents, persisted versions, signatures, and encrypted configuration archives.

Multi-tenant support and microservices remain prohibited.
