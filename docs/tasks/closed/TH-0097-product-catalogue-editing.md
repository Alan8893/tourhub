# TH-0097 — Product Catalogue Editing

Status: DONE

Started: 2026-07-19

Completed: 2026-07-19

Pull request: #107

## Goal

Allow an authorized preparation user to correct shared Product catalogue settings from the Recipe component workflow without recreating the Product or changing existing RecipeComponent quantities.

## Delivered scope

- `PUT /products/{product_id}` updates an active shared Product;
- editable fields are name, category, catalogue unit, and package size;
- Product identifiers and all existing Recipe relationships remain intact;
- the existing unique-name and central alcohol-policy validation boundaries apply to updates;
- missing Product, duplicate name, and prohibited content return explicit API errors;
- the Product dialog supports creation and editing with prefilled values;
- `Изменить продукт` is available next to the selected Product in the Recipe component dialog;
- the edit dialog warns that shared changes affect every Recipe using the Product;
- changing the Product catalogue unit does not convert or rewrite RecipeComponent amount/unit values;
- Product catalogue and Recipe detail queries refresh after a successful save;
- no database migration was introduced and Alembic remains `h10021`.

## Verification

- Backend API tests prove update, relationship preservation, unchanged component amount/unit, duplicate-name rejection, alcohol-policy rejection, and missing Product handling;
- TypeScript unit tests and production build pass;
- real-Chrome Recipe acceptance edits a Product from the component workflow, verifies the request payload, refreshed Recipe detail, unchanged `80 gram` component, updated package metadata, and mobile overflow boundary;
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness all passed on candidate head `4df6ec6ffbd26df0d6af5e003b5d772ebdfd19a1`;
- final exact-head validation is required after this documentation closure and before squash merge.

## Preserved boundaries

- no Product archive/restore UI;
- no unit conversion or implicit recalculation;
- no shopping or historical Project snapshot rewrite;
- no Product ownership model;
- no Recipe-to-Dish synchronization, which is assigned to TH-0098;
- no architecture, runtime, database, or v0.1.0 tag change.
