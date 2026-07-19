# TH-0091 — Central Alcohol Prohibition

Status: DONE

Last updated: 2026-07-19

## Goal

Enforce the approved no-exceptions alcohol prohibition through one Backend domain policy across Product, Recipe, Dish, API, and CSV import paths, and archive existing prohibited catalogue records.

## Delivered

### Central policy

- Unicode NFKC, case-folding, punctuation tokenization, and `ё → е` normalization;
- complete-word matching with Russian case forms and English names;
- safe false-positive boundaries for `ромашка`, `пивные дрожжи`, and `винный уксус`;
- one centrally handled HTTP 422 Russian policy error.

### Runtime boundaries

- prohibited Product creation rejected and archived Products hidden;
- prohibited Recipe names and prohibited/archived Product components rejected;
- Recipe content revalidated before submit, publish, and restore;
- policy-archived Recipe restore blocked;
- prohibited Dish names and prohibited/archived Recipe variants rejected;
- archived Dishes excluded from active catalogues and preparation repositories;
- Product and Recipe CSV preview/apply use the same policy wrapper.

### Existing records and acceptance

- Alembic `h10021` adds Product/Dish archive state and policy markers on Product, Recipe, and Dish;
- existing prohibited Products, dependent Recipes, and default Dishes are archived rather than deleted;
- historical assignments, foreign keys, calculations, and exports remain readable;
- migration downgrade distinguishes policy archival from unrelated manual Recipe archival;
- classifier, API/import, Recipe lifecycle, reversible migration, complete Backend/Frontend, PostgreSQL, and release-runtime acceptance passed;
- ADR-025 accepted and current documentation synchronized.

## Out of scope retained

- fuzzy/external alcohol classifiers;
- user-configurable exceptions or allowlists;
- automatic deletion;
- Product/Dish archive-management UI;
- rewriting historical Project assignments.
