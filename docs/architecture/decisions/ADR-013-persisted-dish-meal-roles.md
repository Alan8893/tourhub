# ADR-013 — Persisted Dish Meal Roles and Meal-Type Compatibility

Status: Accepted

Date: 2026-07-15

## Context

TourHub can persist multiple dishes inside a `MealSlot`, but automatic generation currently treats the active dish catalogue as an undifferentiated pool. Real composition rules need durable metadata for main dishes, additions, drinks, and snack-compatible dishes before the generator can reason about breakfast, snack, lunch, dinner, repeatability, or calendar-day diversity.

A role alone is insufficient. `main` describes the structural purpose of a dish, but does not distinguish breakfast porridge from lunch soup. Without persisted meal-type compatibility, borscht could be selected for breakfast and oatmeal for dinner.

The metadata must not be inferred from Russian names, stored only in frontend state, attached to a transient generation DTO, or coupled to the currently selected recipe. A dish may legitimately serve more than one composition purpose: for example, a sandwich can be an addition to lunch and also a snack.

## Decision

### Ownership

Meal-role metadata and meal-type compatibility belong to `Dish`.

- `Recipe` describes ingredients and preparation and may be replaced without changing the menu purpose of the dish.
- `MealSlotDish` represents a concrete persisted assignment and must not redefine catalogue classification.
- Manual `MealSlotDish` assignments remain authoritative regardless of catalogue roles or compatibility.

### Persistence model

Add normalized role assignments:

```text
dish_meal_roles
  dish_id          FK -> dishes.id, ON DELETE CASCADE
  role             VARCHAR(32)
  is_repeatable    BOOLEAN NOT NULL DEFAULT FALSE

  PRIMARY KEY (dish_id, role)
```

Add normalized compatibility owned by the role assignment:

```text
dish_meal_role_meal_types
  dish_id          VARCHAR
  role             VARCHAR(32)
  meal_type        VARCHAR(32)

  FK (dish_id, role)
    -> dish_meal_roles(dish_id, role)
    ON DELETE CASCADE

  PRIMARY KEY (dish_id, role, meal_type)
```

Allowed role values:

- `main` — the principal cooked or substantial dish;
- `addition` — bread, salad, sandwiches, or another supporting item;
- `drink` — tea, coffee, compote, or another drink;
- `snack` — fruit, sweets, nuts, dried fruit, or another snack item.

Allowed meal types:

- `breakfast`;
- `snack`;
- `lunch`;
- `dinner`.

A dish may have more than one role. Each role must have at least one compatible meal type. Compatibility belongs to `(dish_id, role)`, not to Dish globally, so a sandwich may be `addition` for breakfast/lunch/dinner and independently `snack` for the snack slot.

Role and meal-type values are stored as constrained strings rather than PostgreSQL-native enums so future additive migrations remain straightforward.

`is_repeatable` belongs to the `(dish_id, role)` assignment. This prevents a multi-role dish from becoming repeatable in every context merely because one of its roles may repeat.

### Meaning of common catalogue concepts

- Soup is classified as `main`, normally compatible with `lunch` and/or `dinner`; `soup` is not a composition role.
- Breakfast porridge is `main` compatible with `breakfast`.
- A universal addition is `addition` compatible with the applicable main meal types and has `is_repeatable = true`.
- A repeatable drink is `drink` with `is_repeatable = true` and explicit compatible meal types.
- Unclassified dishes remain valid catalogue and manual-selection records but are not eligible for role-aware automatic selection.

### Backend compatibility matrix

The backend validates persisted compatibility:

| Role | Allowed meal types |
|---|---|
| `main` | `breakfast`, `lunch`, `dinner` |
| `addition` | `breakfast`, `lunch`, `dinner` |
| `drink` | `breakfast`, `lunch`, `dinner` |
| `snack` | `snack` |

The composition plan remains:

| Meal type | Required role plan |
|---|---|
| breakfast | `main`, optional `addition`, optional `drink` |
| snack | `snack` |
| lunch | `main`, optional `addition`, optional `drink` |
| dinner | `main`, optional `addition`, optional `drink` |

A candidate is eligible only when both its role and the current meal type match persisted compatibility. The exact minimum catalogue-readiness thresholds and optional-role behavior belong to the composition policy and tests.

### API contract

The implementation exposes:

```text
DishMealRoleResponse
  role: main | addition | drink | snack
  is_repeatable: boolean
  allowed_meal_types: breakfast[] | snack[] | lunch[] | dinner[]
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
    {
      "role": "addition",
      "is_repeatable": true,
      "allowed_meal_types": ["breakfast", "lunch", "dinner"]
    },
    {
      "role": "snack",
      "is_repeatable": false,
      "allowed_meal_types": ["snack"]
    }
  ]
}
```

The endpoint validates unique roles, non-empty unique meal types, and the compatibility matrix, then replaces the full assignment set transactionally. Existing dish name and active-recipe update semantics remain unchanged.

### Migration and rollout

1. Create both normalized tables with no heuristic data backfill.
2. Expose role and compatibility data through the atomic management API without changing current generation behavior.
3. Classify the active catalogue explicitly through the dish editor or API.
4. Add catalogue-readiness validation per meal type and visible warnings.
5. Enable role-aware deterministic generation only after the persisted metadata path is tested.
6. Keep unclassified dishes available for manual selection.
7. Preserve purchasing recalculation and legacy `MealPlanItem` compatibility throughout rollout.

The migration must never guess roles or compatibility from dish names, recipe names, ingredients, or historical meal placement.

### Generation filtering

For each generated `MealSlot`, the backend will:

1. determine the required role from the composition plan;
2. keep only dishes with that persisted role;
3. keep only role assignments compatible with the current meal type;
4. exclude archived-recipe dishes and apply project restrictions;
5. apply repeatability and calendar-day diversity;
6. choose deterministically or emit a visible readiness warning.

This prevents a lunch-only borscht from appearing at breakfast and a breakfast-only oatmeal from appearing at lunch or dinner.

### Diversity and repeatability

- Three-day diversity is evaluated for `main` selections by trip calendar day, not by selection count.
- `is_repeatable = true` allows the specific role assignment to bypass the corresponding diversity restriction.
- Archived-recipe dishes are excluded from automatic selection regardless of roles.
- Existing manual assignments are not removed or silently replaced by regeneration.

## Consequences

- The role model supports multi-purpose dishes without ambiguous role values.
- Meal-type compatibility prevents structurally valid but contextually wrong selections.
- Recipe replacement does not require reclassifying a dish.
- Role-aware generation can be introduced incrementally without breaking existing deployments.
- Catalogue classification becomes explicit product data that requires UI and API support.
- The generator must handle incomplete role/meal-type catalogues with deterministic warnings rather than hidden fallback assumptions.

## Rejected alternatives

### Single `meal_role` column on `dishes`

Rejected because legitimate multi-role dishes would require lossy classification.

### Global `allowed_meal_types` on Dish

Rejected because compatibility depends on the role. A sandwich may be an addition at main meals and a snack only in the snack slot.

### Roles on `Recipe`

Rejected because recipe variants and active-recipe replacement are preparation concerns, not menu-composition identity.

### Roles on `MealSlotDish`

Rejected because this would classify individual assignments rather than the catalogue and would not support automatic candidate selection.

### Name- or ingredient-based inference

Rejected because it is language-dependent, non-deterministic, and silently corrupts business metadata.

### Separate roles for soup, breakfast-main, or universal addition

Rejected because soup and breakfast-main are compatibility distinctions of `main`, while universal addition is the combination of `addition`, explicit compatibility, and repeatability.

## Supersedes

This ADR supersedes the persistence assumptions in ADR-006 sections 2 and 3. `MealSlot` and `MealSlotDish` are the primary menu-composition persistence model; `MealPlanItem` remains only a legacy compatibility path.
