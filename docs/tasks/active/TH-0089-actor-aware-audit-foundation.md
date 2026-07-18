# TH-0089 — Actor-Aware Audit Foundation

Status: IN PROGRESS

Last updated: 2026-07-19

## Goal

Establish one safe append-only audit boundary with real actor attribution, immutable Recipe moderation history, user-access history, an Administrator query API, and a responsive audit surface.

## Scope

### Persistence

- add `audit_events` through Alembic `h10020`;
- store actor User ID plus display-name, email, and role snapshots;
- store semantic action, entity type/ID, safe before/after/context JSON, and timestamp;
- keep AuditEvent independent from live User foreign-key lifecycle;
- reject normal ORM update and delete attempts;
- keep one Alembic head.

### Backend

- add one bounded recursive sanitizer that removes password, hash, credential, cookie, session, token, authorization, and secret fields;
- record AuditEvent in the same transaction as its business mutation;
- record user role/active-state administration;
- record Recipe submit, publish, and reject transitions;
- expose Administrator-only filtered and paginated reads;
- keep existing focused settings history compatible.

### Frontend

- add an Administrator-only Audit section under Settings;
- show actor snapshot, action, entity, timestamp, and safe changed fields;
- filter by entity type, action, actor ID, and entity ID;
- preserve mobile containment and loading/error/empty states.

### Documentation and acceptance

- add ADR-023;
- add focused Backend tests for attribution, filtering, sanitization, transaction persistence, moderation history, and immutability;
- add focused Chrome acceptance for rendering, filtering, and mobile containment;
- synchronize current architecture, domain, roadmap, status, technical debt, task index, and operator migration head.

## Out of scope

- automatic ORM-wide auditing;
- project, menu, settings, mail, invitation, catalogue, shopping, equipment, and document write-path instrumentation;
- undo or event replay;
- audit export, external SIEM, realtime notifications, and retention UI;
- central alcohol prohibition;
- project ownership, row-level ACLs, multi-tenancy, or live collaboration.

## Definition of done

- critical first-slice actions write actor-attributed events in the same transaction;
- Recipe moderation decisions retain immutable history beyond the latest Recipe fields;
- sensitive values are absent from nested audit payloads;
- AuditEvent has no application mutation API and ORM update/delete attempts fail;
- only Administrator can query the audit API and open the audit UI;
- focused Backend and Chrome acceptance pass;
- `h10020` is the single Alembic head and clean release runtime applies it;
- exact-head repository workflows pass.
