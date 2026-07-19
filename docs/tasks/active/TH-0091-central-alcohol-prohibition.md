# TH-0091 — Central Alcohol Prohibition

Status: IN PROGRESS

Last updated: 2026-07-19

## Goal

Enforce the approved no-exceptions alcohol prohibition through one Backend domain policy across Product, Recipe, Dish, API, and CSV import paths, and archive existing prohibited catalogue records.

## Scope

### Central policy

- normalize Unicode, case, punctuation, and `ё`/`е` consistently;
- classify complete words rather than unsafe substrings;
- support approved Russian and English alcohol terms;
- return one safe Russian HTTP 422 policy error for runtime writes.

### Runtime boundaries

- reject prohibited Product creation;
- hide archived Products from the active catalogue;
- reject prohibited Recipe names and archived/prohibited Product components;
- validate Recipe content before submit, publish, and restore;
- reject prohibited Dish names and prohibited/archived Recipe variants;
- hide archived Dishes from active catalogues and preparation generation;
- apply the same policy during Product and Recipe CSV preview/apply.

### Existing records

- add Product and Dish archive state;
- add an `archived_by_alcohol_policy` marker for Product, Recipe, and Dish;
- archive prohibited Products by name/category;
- archive Recipes by name or prohibited Product component;
- archive Dishes by name or prohibited default Recipe;
- preserve historical relationships and calculations;
- keep the migration reversible without unarchiving unrelated manually archived Recipes.

### Acceptance

- focused classifier tests, including false-positive boundaries;
- Product/Recipe/Dish/import API tests;
- Recipe submit/publish/restore tests;
- `h10020 → h10021 → h10020` migration coverage;
- exact-head repository and clean release runtime validation.

## Out of scope

- fuzzy or external alcohol classification services;
- user-configurable exceptions or allowlists;
- content moderation unrelated to alcohol;
- automatic deletion of historical records;
- Product/Dish archive-management UI;
- changes to previously persisted historical Project assignments.

## Definition of done

- all new Product/Recipe/Dish/API/import paths use one Backend policy;
- existing prohibited catalogue records are archived deterministically;
- archived records remain available to historical foreign-key relationships but are excluded from new selection;
- policy-archived Recipes cannot be restored;
- `h10021` is the single Alembic head;
- focused and complete repository acceptance passes.
