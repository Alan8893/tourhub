# ADR-024 — Consolidated Project Exports

Status: Accepted

Date: 2026-07-19

## Context

TourHub already exports Russian purchase and equipment PDF/XLSX files plus a coordinated ZIP. The approved Product Specification requires one complete PDF and one workbook containing trip parameters, menu, food loadout, shopping, equipment, warnings, and comments. The existing focused artifacts do not satisfy that contract by themselves.

The persisted MealSlotDish Recipe is the historical assignment snapshot. Exporting the current Dish default would reinterpret prepared projects after later catalogue changes.

## Decision

TourHub adds one immutable `ConsolidatedProjectDocumentDTO` assembled by Backend from a single prepared Project read:

- Project parameters;
- MealPlan days, slots, Dish names, and exact selected Recipe names;
- PurchaseList required quantities and packaging;
- PurchaseChecklist progress and comments when present;
- EquipmentList visible rows;
- MealPlan warnings and responsible-person text.

One `ProjectDocumentService` instance resolves one club/document branding snapshot lazily and reuses it for every artifact generated during the same package request.

### PDF

The complete PDF is Russian and contains sections for:

1. parameters;
2. menu by day;
3. loadout;
4. shopping;
5. equipment;
6. warnings and comments.

Landscape A4 is used so packaging and purchase-progress columns remain readable without dropping approved fields.

### Workbook

The complete workbook contains exactly these sheets in order:

1. `Поход`;
2. `Меню`;
3. `Раскладка`;
4. `Закупка`;
5. `Оборудование`.

Document appearance and branding are applied independently to every sheet.

### Compatibility

Existing focused purchase/equipment PDF, XLSX, and print endpoints remain supported. The ZIP includes both complete artifacts and compatibility artifacts. This avoids breaking current operator workflows while making the specification-complete downloads primary in the UI.

## Consequences

- prepared projects can be handed off using one complete PDF or workbook;
- exported menu Recipes remain stable even if Dish defaults change later;
- no schema migration is required;
- package generation remains synchronous and local;
- missing menu, purchasing, or equipment preparation returns a conflict rather than a partial complete export;
- scheduled generation, email delivery, download audit events, and new Recipe metadata remain separate work.
