# TH-0076 — System Settings Document Appearance

Status: DONE

Completed: 2026-07-17

Merged PR: #86

Merge commit: `18d5c9637e2e692b630009167dd622ee40ee2747`

## Goal

Add a typed `Документы` settings section that controls PDF, Excel, printable text, and ZIP branding through one immutable snapshot loaded once per generation request.

## Delivered

- independent singleton `DocumentAppearanceSettings` persistence and Alembic `h10010`;
- validated document palette, logo source, contacts, footer, title background, and table density;
- optimistic versioning, PostgreSQL row locking, HTTP 409 conflicts, and safe history;
- one frozen snapshot from club and document settings per generation request;
- consistent purchase/equipment PDF, XLSX, print, and ZIP rendering;
- responsive Russian settings editor with isolated preview;
- exact-head backend, frontend, browser, PostgreSQL, Docker, document, and operator validation.

## Scope boundary preserved

Consolidated export contents, arbitrary templates, per-project themes, modules, invitations, access, SMTP, and encrypted configuration archives remain separate work.