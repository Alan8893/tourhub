# TH-0090 — Consolidated Russian Export Completeness

Status: IN PROGRESS

Last updated: 2026-07-19

## Goal

Deliver the approved complete Russian PDF and XLSX artifacts for one prepared Project while preserving existing focused purchase/equipment downloads.

## Scope

### Complete PDF

- one branded PDF using one immutable club/document appearance snapshot;
- trip parameters;
- menu by day with persisted Dish and selected Recipe;
- food loadout;
- shopping and packaging;
- equipment;
- warnings, checklist comments, and responsible-person text.

### Complete workbook

- exact Russian sheets `Поход`, `Меню`, `Раскладка`, `Закупка`, and `Оборудование`;
- persisted assignment Recipe names rather than mutable Dish defaults;
- calculated quantities, packaging, purchase progress, surplus, comments, and equipment sources;
- branding and document appearance applied to every sheet.

### Integration

- add consolidated PDF/XLSX download endpoints;
- add complete-download controls to the responsive Documents card;
- include complete artifacts in the coordinated ZIP while keeping compatibility documents;
- add focused Backend and Chrome acceptance.

## Out of scope

- new document persistence or schema changes;
- email delivery or scheduled generation;
- audit instrumentation for document downloads;
- alcohol policy;
- new Recipe metadata not already persisted;
- replacing compatibility purchase/equipment endpoints.

## Definition of done

- PDF contains all approved sections;
- XLSX contains the five approved Russian sheets in order;
- one brand snapshot is reused across one package request;
- package includes complete PDF/XLSX and compatibility artifacts;
- desktop/mobile download controls pass Chrome acceptance;
- current documentation is synchronized;
- exact-head repository workflows pass.
