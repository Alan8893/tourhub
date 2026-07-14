# TourHub Product Specification

Status: Approved

Last updated: 2026-07-14

## 1. Product Scope

TourHub is a local ERP application for one tourist club.

- One installation represents one club.
- Multi-tenant architecture is prohibited.
- MVP runs entirely in the local infrastructure of the club.
- Paid external services are not used.
- The technology stack is changed only after Product Owner approval.

## 2. Access and Roles

Registration is available only through administrator invitations.

MVP roles:

- Administrator;
- Instructor;
- Verified Instructor.

Verified Instructor may:

- publish personal recipes to the club library;
- review recipes submitted by other instructors;
- edit club recipes;
- archive club recipes;
- reject publication with a comment.

Administrator may manage users, roles, invitations, system settings, and recipes. Permanent recipe deletion is allowed only when the recipe has never been used; otherwise recipes are archived.

## 3. Participant Model

MVP stores participant count only.

The participant count may change after menu generation. When it changes:

- selected dishes remain unchanged;
- ingredient quantities are recalculated;
- package quantities are recalculated;
- shopping list quantities are recalculated;
- equipment quantities are recalculated when they depend on group size.

Participant profiles, contacts, and individual characteristics are a future module.

## 4. Meal Schedule

Supported meal types:

- breakfast;
- lunch;
- snack;
- dinner.

For multi-day trips, all intermediate days contain all meal types.

The instructor selects the first meal and the last meal. One-day trips contain only meals inside the selected range. The same first and last meal is allowed.

## 5. Menu Generation and Editing

The menu is generated automatically unless the instructor selects dishes manually.

The instructor may add, remove, and replace dishes. Manual choices always override automatic generation rules.

MVP diversity rules:

- the same main dish should not repeat within three days;
- the same dish should not be used twice on one day;
- drinks, bread, tea, coffee, and universal additions may repeat;
- instructor preferences increase selection priority but do not disable diversity;
- when the catalogue is insufficient, repetition is allowed with a warning.

Changing participant count does not regenerate selected dishes.

## 6. Dishes and Recipes

Dish and Recipe are separate entities.

One Dish may have multiple Recipe variants.

Recipe scopes:

- CLUB — approved club standard;
- PERSONAL — instructor-specific recipe;
- ARCHIVED — retained for history but excluded from generation.

Generation modes:

- club recipes only;
- club and personal recipes;
- personal recipes preferred.

A recipe may include:

- components and ingredients;
- preparation technology;
- notes;
- required equipment;
- tags;
- categories;
- season compatibility;
- dietary restrictions;
- practical hiking quantity rules.

## 7. Quantities and Packaging

MVP supports:

- gram;
- kilogram;
- millilitre;
- litre;
- piece;
- can;
- package;
- portion;
- head;
- pack.

The primary quantity rule is amount per person. Existing fixed-group and package-per-people rules remain supported where required by hiking recipes.

Package count is always rounded up. The system stores:

- required quantity;
- package size;
- number of packages;
- purchased quantity;
- remainder.

Example: 2500 g required, 900 g package size, 3 packages, 2700 g purchased, 200 g remainder.

## 8. Shopping

Shopping list is recalculated automatically after menu or participant-count changes.

Identical products from different recipes are aggregated.

MVP shopping item fields:

- required quantity;
- unit;
- package size;
- package count;
- purchased quantity;
- remainder;
- category;
- purchased status;
- comment;
- optional responsible person text.

Prices, shop selection, stock balances, and price aggregator integration are future work.

## 9. Equipment

Equipment is part of MVP.

- Equipment requirements are attached to recipes.
- Identical equipment is aggregated.
- Quantity is calculated as the maximum simultaneously required amount, not the sum across all trip days.
- Instructor may manually add, remove, or change equipment quantity.
- Warehouse accounting, issue workflow, and participant distribution are future modules.

## 10. Exports

PDF export contains:

- club logo from system settings;
- trip parameters;
- menu by day;
- food loadout;
- shopping list;
- equipment list;
- warnings and comments.

Excel export contains sheets:

- `Поход`;
- `Меню`;
- `Раскладка`;
- `Закупка`;
- `Оборудование`.

UI and exports are in Russian for MVP.

## 11. Audit Log

MVP keeps an audit trail for:

- project changes;
- participant-count changes;
- menu editing;
- recipe editing;
- recipe publication and archiving;
- user and role administration.

The audit log stores actor, action, timestamp, and safe change metadata. Passwords, tokens, and sensitive secret values must never be logged.

## 12. Alcohol Prohibition

Alcohol is prohibited without exceptions.

- Alcohol products cannot be created.
- Alcohol cannot be added to recipes.
- Alcoholic dishes and drinks are rejected.
- Import and API validation apply the same rule.
- Existing prohibited records are archived.

This is a backend domain rule and cannot rely only on frontend validation.

## 13. Runtime and Operations

Required local startup command:

```bash
docker compose up --build
```

The local stack includes frontend, backend, PostgreSQL, Redis when required by implemented features, and Swagger/OpenAPI.

The repository provides documented backup and restore commands. Scheduled backup is external to the application and may use cron or the operating-system scheduler.

## 14. Product Priorities

Priority order:

1. Stability.
2. User experience.
3. Architectural clarity.
4. Feature completeness.
5. Release speed.
