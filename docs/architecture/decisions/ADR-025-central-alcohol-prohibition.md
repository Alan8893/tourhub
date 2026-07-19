# ADR-025 — Central Alcohol Prohibition

Status: Accepted

Date: 2026-07-19

## Context

The approved Product Specification prohibits alcohol without exceptions. Product, Recipe, Dish, API, and import validation must use the same Backend rule, and existing prohibited records must be archived rather than deleted.

Product and Dish did not contain a semantic alcohol flag. Existing catalogue data therefore requires deterministic classification from persisted names/categories and Recipe composition. Naive substring search is unsafe because `ром` must not match `ромашка`, while ordinary Russian cases such as `ромом` must be recognized.

## Decision

TourHub introduces one versioned Backend `AlcoholPolicy`.

### Classification

- text is normalized with Unicode NFKC, case-folding, and `ё → е`;
- punctuation separates tokens;
- prohibited terms match complete normalized words only;
- the versioned vocabulary contains common Russian nouns/case forms and English alcohol names/categories;
- broad adjectives are not treated as proof by themselves, so `пивные дрожжи` and `винный уксус` are not false positives;
- no user exceptions, overrides, or allowlists are supported.

### Runtime validation

The same policy is applied to:

- Product creation;
- Recipe creation/rename and Product component writes;
- Recipe submit, publish, and restore activation paths;
- Dish creation/update and every selected Recipe variant;
- Product and Recipe CSV preview/apply.

`AlcoholPolicyViolation` is handled centrally as HTTP 422 with a bounded Russian message. Frontend validation may guide users later but never replaces this Backend rule.

### Existing-record handling

Alembic `h10021` adds:

- `Product.is_archived` and `Product.archived_by_alcohol_policy`;
- `Dish.is_archived` and `Dish.archived_by_alcohol_policy`;
- `Recipe.archived_by_alcohol_policy` alongside its existing archive state.

The migration archives:

1. Products matching name/category policy;
2. Recipes matching their name or containing a prohibited Product;
3. Dishes matching their name or using a prohibited Recipe as default.

Policy-archived records are retained for historical foreign keys and exports but excluded from active catalogues and new preparation selection. A valid Dish is not archived merely because one non-default variant becomes archived; that Recipe becomes unavailable for future attachment/generation.

The marker distinguishes policy archival from ordinary archive state, prevents policy-archived Recipe restoration, and supports a reversible migration without unarchiving unrelated manually archived Recipes.

## Consequences

- one deterministic rule protects every approved runtime/import boundary;
- existing prohibited records are retained but inactive;
- historical Project assignments and calculations remain readable;
- active Product and Dish catalogues require archive filtering;
- Product/Dish archive-management UI is not added in this slice;
- fuzzy/external classification is not part of the current release;
- later vocabulary changes require reviewed policy and data-migration updates.
