# TH-0090 — Consolidated Russian Export Completeness

Status: DONE

Last updated: 2026-07-19

## Goal

Deliver the approved complete Russian PDF and XLSX artifacts for one prepared Project while preserving existing focused purchase/equipment downloads.

## Delivered

### Complete PDF

- one branded landscape PDF using one immutable club/document appearance snapshot;
- Project parameters;
- menu by day with persisted Dish and exact selected Recipe;
- food loadout;
- shopping, packaging, surplus, checklist progress, and comments;
- equipment and source labels;
- warnings and responsible-person text.

### Complete workbook

- exact Russian sheets `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование` in order;
- persisted assignment Recipe names rather than mutable Dish defaults;
- calculated quantities, packaging, purchase progress, surplus, comments, and equipment sources;
- branding and document appearance applied to every sheet.

### Integration and acceptance

- consolidated PDF/XLSX download endpoints;
- primary complete-download controls in the responsive Documents card;
- complete artifacts included in the coordinated ZIP together with compatibility documents;
- focused Backend generator/API/package tests;
- complete Frontend browser suite including desktop/mobile consolidated-download acceptance;
- ADR-024 accepted and current documentation synchronized;
- no schema migration; Alembic head remains `h10020`.

## Out of scope retained

- document persistence or signatures;
- email delivery or scheduled generation;
- audit instrumentation for document downloads;
- central alcohol policy;
- new Recipe metadata;
- replacement of compatibility purchase/equipment endpoints.
