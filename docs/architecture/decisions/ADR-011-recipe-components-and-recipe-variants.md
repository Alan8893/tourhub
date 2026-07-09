# ADR-011 — Recipe Components and Recipe Variants

Status: Accepted

Date: 2026-07-09

## Context

The original recipe model used:

Recipe → Ingredient → Product

This model was sufficient for simple calculations but could not represent hiking cooking scenarios where products have different roles.

Examples:

- rice as a base component;
- salt as a cooking component;
- crackers as optional component;
- sour cream as serving add-on.

## Decision

Introduce RecipeComponent as the new recipe composition layer.

Target model:

Dish
↓
Recipe
↓
RecipeComponent
↓
Product

## Component Types

RecipeComponent supports:

- BASE
- COOKING
- OPTIONAL
- SERVING_ADD_ON

## Migration Strategy

Migration is evolutionary.

Ingredient remains as a legacy compatibility model during transition.

New calculations use RecipeComponent first.

Old consumers must not break.

## Consequences

Positive:

- richer recipe domain;
- correct hiking calculations;
- support for optional products;
- future recipe variants.

Negative:

- temporary duplication between Ingredient and RecipeComponent.

## Calculation Rules

Supported modes:

- per_person;
- fixed_group;
- package_per_people.
