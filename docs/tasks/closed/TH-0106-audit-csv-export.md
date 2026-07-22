# TH-0106 — Audit CSV Export

Status: DONE

## Goal

Allow an active Administrator to export the append-only audit journal as a UTF-8 CSV file using the same Backend-owned filters as the existing Audit UI.

## Delivered scope

- one Administrator-only Backend endpoint at `/api/v1/audit/events/export.csv`;
- shared actor, entity type, entity ID, action, created-from, and created-to filter semantics in `AuditService`;
- deterministic columns for actor snapshot, semantic action, entity identity, timestamp, and already-sanitized before/after/context JSON payloads;
- UTF-8 BOM for Russian spreadsheet review;
- spreadsheet-formula neutralization for every exported cell;
- explicit 10,000-row maximum with a clear bounded error;
- Audit UI date filters, `Скачать CSV`, loading state, and visible export failure feedback;
- Backend policy tests, Frontend helper tests, and dedicated real-Chrome acceptance;
- no migration; current Alembic head remains `h10023`;
- immutable `v0.1.0` remains unchanged.

## Backend policy

- `/api/v1/audit/*` remains Administrator-only through the centralized router dependency;
- React does not own authorization, filter correctness, row limits, sanitization, or CSV shape;
- export contains only values persisted in `AuditEvent` and never rehydrates protected domain data;
- JSON cells use deterministic UTF-8 serialization;
- exports are read-only and create no recursive `audit_exported` event;
- no persistence or transaction boundary changes were introduced.

## Non-goals retained

- audit retention, deletion, cleanup, archive, or retention-policy UI;
- external SIEM delivery, scheduled exports, background jobs, diagnostics, undo, or event replay;
- new audit actions or broader audit coverage;
- exporting hidden credentials, tokens, cookies, raw request bodies, source CSV uploads, generated document contents, phone numbers, or social URLs;
- session administration, Product/Dish archive-management UI, ownership-aware import UX, or Project copy;
- multi-tenant support, microservices, or changes to the immutable `v0.1.0` tag.

## Acceptance coverage

### Backend

- filtered CSV contains the matching events selected by the shared filter policy;
- UTF-8 BOM, deterministic headers, Russian text, and deterministic JSON are verified;
- formula-like actor/entity values are escaped;
- excessive exports fail with HTTP 422;
- non-Administrators cannot export audit data;
- export does not append an AuditEvent or mutate domain state;
- existing safe-payload sanitization and rollback coverage remains part of the full Backend suite.

### Frontend

- Audit can filter by date/time in addition to existing filters;
- `Скачать CSV` sends the active filter set and saves the Backend filename;
- export loading and error states do not block ordinary browsing;
- helper tests cover date normalization and response filename handling.

### Real Chrome

- Administrator opens the Audit surface;
- applies a semantic action filter;
- starts CSV download through the real browser;
- the observed request contains the active filter;
- the returned UTF-8 CSV contains the expected actor, action, and Russian context;
- accepted mobile width has no horizontal overflow.

## Migration

No migration was added. Current Alembic head remains `h10023`.
