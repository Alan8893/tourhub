# TH-0089 — Actor-Aware Audit Foundation

Status: DONE

Last updated: 2026-07-19

## Goal

Establish one safe append-only audit boundary with real actor attribution, immutable Recipe moderation history, user-access history, an Administrator query API, and a responsive audit surface.

## Delivered

- added append-only `audit_events` persistence through Alembic `h10020`;
- stored actor User ID, display-name, email, and role snapshots at action time;
- stored semantic action, entity type/ID, bounded safe before/after/context JSON, and timestamp;
- rejected normal ORM update and delete attempts;
- recorded user role/active-state administration and Recipe submit/publish/reject transitions in the owning transaction;
- exposed Administrator-only filtered and paginated reads;
- added an Administrator Audit section under Settings with responsive filters and changed-field presentation;
- accepted ADR-023 and synchronized current architecture, domain, roadmap, status, technical debt, task index, README, and operator migration head;
- added focused Backend and Chrome acceptance for attribution, filtering, safe payloads, moderation history, immutability, and mobile containment.

## Explicit boundary

The foundation currently instruments user role/activation changes and Recipe submit/publish/reject transitions. Project, menu, settings, mail, invitation, catalogue/import, shopping, equipment, and document write paths require later explicit semantic instrumentation.

Automatic ORM-wide auditing, undo, event replay, audit export, external SIEM, realtime notifications, retention UI, central alcohol prohibition, project ownership, row-level ACLs, multi-tenancy, and live collaboration remain out of scope.

## Verification

Implementation head `a6575b1975480a3e8b48e0aa003963820276762f` passed Quality #974, Document Quality #587, Guided Release Acceptance #538, Operator Docs #524, and Docker Release Runtime #519.

The clean PostgreSQL 18 release stack applied `h10020`, verified the API proxy, restarted application containers, and preserved data after restart.
