# TourHub Current Domain Model

Status: Active

Last updated: 2026-07-14

## 1. Purpose

This document is the concise canonical domain baseline for the MVP. `DOMAIN.md` remains an extended reference. When they conflict, this document, `PRODUCT_SPEC.md`, and accepted ADRs take precedence.

## 2. Club and Access

One TourHub installation represents one tourist club.

There is no tenant selection, tenant identifier, or organization isolation layer in MVP.

Access is invitation-only.

Roles:

- Administrator;
- Instructor;
- Verified Instructor.

Administrator manages users, roles, invitations, system settings, and recipes.

Verified Instructor may publish personal recipes into the club library, review submissions, edit club recipes, archive club recipes, and reject publication with a comment.

Instructor may manage projects, personal recipes, menu choices, shopping state, equipment overrides, and exports within granted permissions.

## 3. Project

Project is the working preparation object for one trip.

MVP stores:

- name;
- start and end dates;
- participant count;
- first and last meal;
- comments;
- preparation results.

Participant count may change after generation. Selected dishes remain unchanged while quantities, packages, shopping, and dependent equipment are recalculated.

Participant profiles and personal information are a future domain.

## 4. Meal Schedule

Meal types:

- breakfast;
- lunch;
- snack;
- dinner.

For multi-day trips, intermediate days contain all meal types. The instructor selects the first and last meal. One-day trips contain only the selected inclusive range, including a single meal when both boundaries are equal.

## 5. Meal Plan and Meal Slot

MealPlan contains days. A MealSlot represents one meal occurrence and contains one or more dishes.

Instructor may:

- add a dish;
- remove a dish;
- replace a dish;
- manually choose dishes before or after generation.

Manual choices override generation rules.

Diversity rules:

- a main dish should not repeat within three days;
- the same dish should not occur twice on one day;
- drinks and universal additions may repeat;
- instructor preferences increase priority but do not disable diversity;
- insufficient catalogue allows repetition with a warning.

## 6. Dish and Recipe

Dish describes the culinary concept. Recipe describes one concrete preparation variant.

One Dish may have many Recipes.

Recipe scopes:

- `CLUB` — approved club standard;
- `PERSONAL` — instructor-specific variant;
- `ARCHIVED` — retained for history and excluded from generation.

Generation modes:

- club recipes only;
- club and personal recipes;
- personal recipes preferred.

Recipe may contain:

- components and ingredients;
- preparation technology;
- notes;
- equipment;
- tags and categories;
- season compatibility;
- dietary metadata;
- practical hiking quantities.

A club recipe used by historical projects is archived rather than destructively deleted.

## 7. Product and Quantity

Product is a catalogue item independent of recipes.

Supported units include gram, kilogram, millilitre, litre, piece, can, package, portion, head, and pack.

The primary MVP rule is amount per participant. Existing fixed-group and package-per-people rules remain valid for practical hiking recipes.

Alcohol is prohibited without exceptions. Backend rejects alcoholic products, dishes, drinks, recipe components, and imports. Existing prohibited records are archived.

## 8. Shopping and Packaging

Identical products are aggregated across recipe components.

Package count is rounded upward.

For every item, the system may expose:

- required quantity;
- unit;
- package size;
- package count;
- purchased quantity;
- remainder;
- category;
- purchased status;
- comment;
- optional responsible person.

Prices, stores, warehouse balances, and external price aggregators are future work.

## 9. Equipment

Equipment requirements originate from recipes.

Identical items are aggregated by maximum simultaneous requirement rather than summed across the whole trip.

Instructor may manually add, remove, or change an equipment quantity.

Warehouse issue workflow and participant distribution are future domains.

## 10. Documents

MVP exports Russian PDF and Excel documents.

PDF includes club branding, trip parameters, menu, food loadout, shopping, equipment, warnings, and comments.

Excel includes sheets for trip, menu, loadout, shopping, and equipment.

Club logo and name come from system settings.

## 11. Audit Log

Audit events include:

- user, role, and invitation administration;
- project and participant-count changes;
- menu editing;
- recipe editing, publication, rejection, and archiving;
- other security-sensitive or business-significant changes.

Audit records actor, action, timestamp, and safe metadata. Passwords, tokens, invitation secrets, and sensitive values are never stored in the log.

## 12. Future Domains

- participant profiles;
- routes and GPX;
- logistics and load distribution;
- warehouse balances;
- procurement prices and aggregator integration.

Multi-tenant support is not a future domain and remains prohibited.
