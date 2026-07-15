# ADR-013 — Persisted Dish Meal Roles

Status: Accepted

Date: 2026-07-15

## Context

TourHub can persist multiple dishes inside a `MealSlot`, but automatic generation currently treats the active dish catalogue as an undifferentiated pool. Real composition rules need durable metadata for main dishes, additions, drinks, and snack-compatible dishes before the generator can reason about breakfast, snack, lunch, dinner, repeatability, or calendar-day diversity.

The metadata must not be inferred from Russian names, stored only in frontend state, attached to a transient generation DTO, or coupled to the currently selected recipe. A dish may legitimately serve more than one composition purpose: for example, a sandwich can be an addition to lunch and also a snack.

## Decision

### Ownership

Meal-role metadata belongs to `Dish`.

- `Recipe` describes ingredients and preparation and may be replaced without changing the menu purpose of the dish.
- `MealSlotDish` represents a concrete persisted assignment and must not redefine catalogue classification.
- Manual `MealSlotDish` assignments remain authoritative regardless of catalogue roles.

### Persistence model

Add a normalized table named `dish_meal_roles`:

```text
dish_meal_roles
  dish_id          FK -> dishes.id, ON DELETE CASCADE
  role             VARCHAR(32)
  is_repeatable    BOOLEAN NOT NULL DEFAULT FALSE

  PRIMARY KEY (dish_id, role)
```

Allowed role values:

- `main` — the principal cooked or substantial dish;
- `addition` — bread, salad, sandwiches, or another supporting item;
- `drink` — tea, coffee, compote, or another drink;
- `snack` — fruit, sweets, nuts, dried fruit, or another snack item.

A dish may have more than one role. Role values are stored as constrained strings rather than a PostgreSQL-native enum so future additive migrations remain straightforward.

`is_repeatable` belongs to the `(dish_id, role)` assignment. This prevents a multi-role dish from becoming repeatable in every context merely because one of its roles may repeat.

### Meaning of common catalogue concepts

- Soup is classified as `main`; `soup` is not a composition role.
- A universal addition is represented as `addition` with `is_repeatable = true`; it is not a separate role.
- A repeatable drink is represented as `drink` with `is_repeatable = true`.
- Unclassified dishes remain valid catalogue and manual-selection records but are not eligible for role-aware automatic selection.

### Backend rule matrix

Meal-type compatibility is a backend domain rule, not duplicated per dish:

| Meal type | Required role plan |
|---|---|
| breakfast | `main`, optional `addition`, optional `drink` |
| snack | `snack` |
| lunch | `main`, optional `addition`, optional `drink` |
| dinner | `main`, optional `addition`, optional `drink` |

The exact minimum catalogue-readiness thresholds and optional-role behavior belong to the composition policy and tests. They must use only persisted role assignments.

### API contract

The first implementation adds:

```text
DishMealRoleResponse
  role: main | addition | drink | snack
  is_repeatable: boolean
```

`DishResponse` includes `meal_roles: DishMealRoleResponse[]`.

Role editing uses a dedicated atomic replacement endpoint:

```text
PUT /api/v1/dishes/{dish_id}/meal-roles
```

Request body:

```json
{
  "roles": [
    {"role": "addition", "is_repeatable": true},
    {"role": "snack", "is_repeatable": false}
  ]
}
```

The endpoint validates unique roles and replaces the full assignment set transactionally. Existing dish name and active-recipe update semantics remain unchanged.

### Migration and rollout

1. Create `dish_meal_roles` with no heuristic data backfill.
2. Expose role data and the atomic role-management API without changing current generation behavior.
3. Classify the active catalogue explicitly through the dish editor or API.
4. Add catalogue-readiness validation and visible warnings.
5. Enable role-aware deterministic generation only after the persisted metadata path is tested.
6. Keep unclassified dishes available for manual selection.
7. Preserve purchasing recalculation and legacy `MealPlanItem` compatibility throughout rollout.

The migration must never guess roles from dish names, recipe names, ingredients, or historical meal placement.

### Diversity and repeatability

- Three-day diversity is evaluated for `main` selections by trip calendar day, not by selection count.
- `is_repeatable = true` allows the specific role assignment to bypass the corresponding diversity restriction.
- Archived-recipe dishes are excluded from automatic selection regardless of roles.
- Existing manual assignments are not removed or silently replaced by regeneration.

## Consequences

- The role model supports multi-purpose dishes without adding ambiguous role values.
- Recipe replacement does not require reclassifying a dish.
- Role-aware generation can be introduced incrementally without breaking existing deployments.
- Catalogue classification becomes explicit product data that requires UI and API support.
- The generator must handle incomplete role catalogues with deterministic warnings rather than hidden fallback assumptions.

## Rejected alternatives

### Single `meal_role` column on `dishes`

Rejected because legitimate multi-role dishes would require lossy classification.

### Roles on `Recipe`

Rejected because recipe variants and active-recipe replacement are preparation concerns, not menu-composition identity.

### Roles on `MealSlotDish`

Rejected because this would classify individual assignments rather than the catalogue and would not support automatic candidate selection.

### Name- or ingredient-based inference

Rejected because it is language-dependent, non-deterministic, and silently corrupts business metadata.

### Separate roles for soup or universal addition

Rejected because soup is a kind of main dish, while universal addition is the combination of `addition` and explicit repeatability.

## Supersedes

This ADR supersedes the persistence assumptions in ADR-006 sections 2 and 3. `MealSlot` and `MealSlotDish` are the primary menu-composition persistence model; `MealPlanItem` remains only a legacy compatibility path.