# TH-0106 — Audit CSV Export

Status: IN PROGRESS

## Goal

Allow an active Administrator to export the append-only audit journal as a UTF-8 CSV file using the same Backend-owned filters as the existing Audit UI.

## Scope

- add one Administrator-only Backend endpoint for CSV export;
- reuse the existing audit filters: actor, entity type, entity ID, action, created-from, and created-to;
- keep filter semantics centralized in `AuditService` so list and export cannot diverge;
- export deterministic columns for actor snapshot, semantic action, entity identity, timestamp, and the already-sanitized before/after/context JSON payloads;
- harden spreadsheet cells against formula execution;
- impose a bounded maximum export size and return a clear error instead of producing an unbounded response;
- add a Frontend export action on the existing Audit surface, including date filters and visible failure feedback;
- cover Backend policy, Frontend behavior, and real-Chrome download acceptance;
- keep `v0.1.0` fixed and keep Alembic at one head.

## Backend policy

- `/api/v1/audit/*` remains Administrator-only through the existing centralized router dependency;
- the export endpoint never trusts React to enforce authorization or filter correctness;
- the export contains only values already persisted in `AuditEvent`; it does not rehydrate protected domain data;
- JSON cells are deterministic UTF-8 text and every CSV cell is neutralized when it could be interpreted as a spreadsheet formula;
- exports are read-only and create no new AuditEvent, so downloading history cannot recursively mutate the journal;
- no persistence or transaction boundary changes are introduced.

## Non-goals

- audit retention, deletion, cleanup, archive, or retention-policy UI;
- external SIEM delivery, scheduled exports, background jobs, diagnostics, undo, or event replay;
- new audit actions or broader audit coverage;
- exporting hidden credentials, tokens, cookies, raw request bodies, CSV uploads, generated document contents, phone numbers, or social URLs;
- multi-tenant support, microservices, or changes to the immutable `v0.1.0` tag;
- Project copy.

## Acceptance

### Backend

- filtered CSV contains the same matching events as the list query;
- UTF-8 BOM, deterministic headers, Russian text, and deterministic JSON are verified;
- formula-like actor/entity values are escaped;
- excessive exports fail with a bounded HTTP error;
- an Instructor cannot export audit data;
- export does not append an `audit_exported` event or mutate domain state;
- existing safe-payload sanitization and rollback tests remain green.

### Frontend

- the Audit page can filter by date/time in addition to existing filters;
- `Скачать CSV` sends the active filter set to Backend and saves the returned file;
- export loading and error states are visible and do not block ordinary audit browsing;
- layout remains usable without horizontal overflow at accepted mobile width.

### Real Chrome

- Administrator opens the Audit surface;
- applies a semantic action filter;
- downloads CSV through the real browser;
- the request contains the active filter and the downloaded file contains expected UTF-8 audit data;
- mobile layout has no horizontal overflow.

## Migration

No migration is expected. Current Alembic head remains `h10023` unless implementation proves persistence is required.
