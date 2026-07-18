# ADR-023 — Actor-Aware Audit Foundation

Status: Proposed

Date: 2026-07-19

## Context

TourHub already has small focused history tables for selected System Settings sections, but those records use a generic actor label and are intentionally trimmed. Recipe moderation stores only the latest decision on Recipe. These mechanisms cannot answer who performed a critical action, which role they held at that moment, or how the protected state changed over time.

A global automatic ORM interceptor was considered and rejected for the first slice. It would produce technically complete but semantically weak `updated` events, capture noisy internal persistence, and make secret filtering and transaction ownership harder to verify.

## Decision

TourHub adds an explicit append-only `AuditEvent` boundary.

Each event stores:

- immutable numeric event ID and timestamp;
- actor User ID when available;
- actor display name, email, and role copied at action time;
- semantic action name;
- entity type and stable entity ID;
- bounded safe `before`, `after`, and context JSON.

Actor snapshots intentionally do not depend on a live User foreign key. Historical identity remains readable after later account changes or retention operations.

### Transaction boundary

A service records an AuditEvent in the same SQLAlchemy Session before committing the business change. The business mutation and event therefore commit or roll back together.

Audit rows have no update or delete application API. ORM update and delete operations raise an error. Operational database backup, restore, and approved retention work remain outside normal application actions.

### Sensitive data boundary

Audit normalization removes keys related to passwords, hashes, credentials, cookies, sessions, tokens, authorization values, and secrets at every nested level. Binary values are represented only by their size. Strings, collections, and nesting are bounded.

Raw session values, invitation values, password hashes, SMTP secrets, protocol transcripts, and arbitrary request bodies must never be written to AuditEvent.

### Query boundary

Only Administrator may query `/api/v1/audit/events`. The first API supports filters by actor User ID, entity type, entity ID, action, and time range with bounded pagination.

### First instrumented domains

TH-0089 records semantic events for:

- user role and active-state administration;
- Recipe submission;
- Recipe publication;
- Recipe rejection with its safe decision state.

This replaces the missing immutable moderation history for these transitions. Existing focused settings history remains compatible and is not deleted in this slice.

Projects, menu edits, settings, mail operations, invitations, catalogue changes, shopping, equipment, and document-generation actions require later explicit instrumentation against this shared boundary.

## Consequences

- critical first-slice actions have real actor attribution and immutable before/after history;
- moderation history is no longer limited to the latest Recipe fields;
- auditing remains semantic and transaction-aware rather than a noisy database diff;
- secret filtering has one reusable Backend implementation;
- Administrator receives a responsive filtered audit surface;
- audit coverage is intentionally incomplete until later domain instrumentation slices are delivered;
- undo, event replay, audit export, SIEM integration, realtime notifications, multi-tenancy, and project ACLs remain out of scope.
