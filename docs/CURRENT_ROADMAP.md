# TourHub Current Roadmap

Status date: 2026-07-19

## Product goal

Operate and improve the released local ERP for one tourist club without changing the modular-monolith architecture, single-club boundary, or immutable v0.1.0 tag.

```text
Released first-release sequence
  → v0.1.0
  → Post-release semantic audit coverage
      → TH-0094 Project and Menu Audit Instrumentation
```

## RELEASED — v0.1.0

The complete first-release sequence is delivered through TH-0093 and tagged at exact commit `8bcc2d2d9414d812d81634330034b15121c8442f`.

Released capabilities include:

- complete guided Project preparation through shopping, equipment, readiness, consolidated Russian PDF/XLSX, compatibility files, and ZIP;
- production-like local runtime, backup/restore, recovery, health, LAN access, and restart persistence;
- typed System Settings, invitation-only Access, server sessions, roles, users, SMTP delivery, and multi-user readiness;
- CLUB/PERSONAL Recipe ownership, lifecycle/moderation, Dish variants, generation modes, and persisted assignment Recipes;
- append-only actor-aware AuditEvent foundation with user-access and Recipe moderation events;
- complete Project export contract;
- centralized no-exceptions alcohol policy and reversible `h10021` archival migration;
- Product Acceptance, feature freeze, final PostgreSQL cycle, deployment checklist, exact-head release gates, and tag `v0.1.0`.

## ACTIVE POST-RELEASE

### TH-0094 — Project and Menu Audit Instrumentation

Goal: implement the highest-priority remaining Product Spec audit coverage through the existing ADR-023 foundation.

Planned coverage:

- Project creation and supported Project parameter changes;
- participant-count changes represented in safe before/after snapshots;
- menu generation and regeneration;
- manual MealSlot Dish add, replace, and remove operations;
- authenticated actor snapshots;
- semantic snake_case actions and explicit entity/context IDs;
- business mutation and AuditEvent in one transaction;
- existing Administrator Audit API/UI compatibility;
- no migration, no new menu capability, and Alembic head `h10021`.

## Deferred after TH-0094

### Remaining audit coverage

- System Settings and mail operations;
- invitation creation, revocation, acceptance, and delivery results;
- catalogue/import, shopping, equipment, and document-generation writes;
- audit export, retention UI, SIEM, undo, and replay.

### Product and operations

- participant profiles, routes/GPX, warehouse balances, issue workflow, participant distribution, procurement prices, shops, stock balances, and external aggregators;
- session administration, account recovery, user profiles, asynchronous mail, bounce handling, advanced templates, and attachments;
- moderation notifications, richer Recipe metadata, per-meal Recipe switching, and preference weights;
- scheduled/emailed documents, signatures, Product/Dish archive-management UI, and encrypted configuration archives;
- additional same-origin request hardening only if deployment expands beyond the trusted-LAN model;
- external identity providers and MFA.

Multi-tenant support and microservices remain prohibited. No deferred item becomes active without a separate task.
