# TourHub Project Status

Status date: 2026-07-19

## Current phase

TourHub v0.1.0 is released at exact tag commit `8bcc2d2d9414d812d81634330034b15121c8442f` and Alembic head `h10021`.

TH-0094 Project and Menu Audit Instrumentation is the first active post-release debt-reduction slice. It extends the existing ADR-023 AuditEvent foundation to Product Spec-required Project changes, participant-count changes, menu generation/regeneration, and manual menu edits without changing the released workflow or schema.

## Verified v0.1.0 baseline

- tag `v0.1.0` points exactly to squash-merge commit `8bcc2d2d9414d812d81634330034b15121c8442f`;
- previous Alembic revision is `h10020` and released head is `h10021`;
- complete guided Project preparation, shopping, equipment, readiness, Russian PDF/XLSX, compatibility files, and coordinated ZIP;
- production-like local runtime, backup/restore, recovery, health checks, same-origin API proxy, LAN access, and restart persistence;
- typed System Settings, invitation-only Access, server-owned sessions, roles, users, working SMTP delivery, and multi-user readiness;
- CLUB/PERSONAL Recipe ownership, lifecycle, moderation, Dish variants, generation modes, and assignment Recipe snapshots;
- append-only actor-aware AuditEvent foundation with current user-access and Recipe moderation coverage;
- centralized no-exceptions alcohol policy and reversible `h10021` archival migration;
- Product Acceptance, Release Readiness, PostgreSQL 18 final migration cycle, deployment checklist, exact-head main workflows, and automated release tag evidence.

## Active post-release work

TH-0094 adds semantic audit events owned by existing Project and Menu services:

- Project creation and supported parameter updates;
- participant-count changes visible in before/after snapshots;
- menu generation and regeneration;
- manual MealSlot Dish add, replace, and remove operations;
- real authenticated actor snapshots;
- safe whitelisted before/after/context data;
- one transaction for each business mutation and AuditEvent;
- compatibility with the existing Administrator-only Audit API/UI.

No migration is planned; Alembic head remains `h10021`.

## Remaining deferred non-blocking debt

- audit instrumentation for settings, mail, invitations, catalogue/import, shopping, equipment, and document-generation writes;
- ownership-aware import UX, Product/Dish archive-management UI, and reviewed policy-vocabulary evolution;
- moderation notifications, session administration, account recovery, asynchronous delivery, and bounce handling;
- richer Recipe metadata, per-meal Recipe switching, and preference weights;
- audit export, retention UI, SIEM, undo, and replay;
- participant profiles, routes/GPX, warehouse balances, procurement prices, and external aggregators;
- scheduled/emailed documents, signatures, and encrypted configuration archives.

The released v0.1.0 tag is immutable. Post-release work is delivered only through separately reviewed tasks and later version decisions.
