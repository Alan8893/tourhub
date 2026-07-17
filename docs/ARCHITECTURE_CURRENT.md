# TourHub Current Architecture

Status: Active

Last updated: 2026-07-17

## 1. Purpose

This document is the concise canonical architecture baseline for the implemented MVP. `ARCHITECTURE.md` remains an extended reference. When they conflict, this document and accepted ADRs take precedence.

`PRODUCT_SPEC.md` describes approved target scope. Features marked as deferred here are not yet implemented.

## 2. Deployment

- One installation represents exactly one tourist club.
- Multi-tenant architecture is prohibited.
- The application is a modular monolith.
- PostgreSQL is the production database.
- SQLite may be used only in tests.
- The release stack uses built backend/frontend images without application source bind mounts.
- PostgreSQL and Redis remain internal to the release Compose network.
- Paid external services are not used.

## 3. Application boundaries

### Frontend

React, TypeScript, Vite, Material UI, TanStack Query, and React Router.

Frontend contains presentation, form state, responsive navigation, isolated previews, file selection, local display-mode preference, and API integration. It does not own quantity calculations, menu generation, shopping aggregation, import validation, settings policy, contrast acceptance, secret handling, or authorization decisions.

The application layout uses a temporary drawer on mobile and a permanent sidebar on larger screens. System Settings uses vertical section navigation on desktop and a section selector on mobile.

Saved appearance is applied through one global dynamic Material UI ThemeProvider. An unsaved appearance draft is rendered only inside an isolated nested ThemeProvider and must not modify the rest of the application before successful backend validation and save.

### Backend

FastAPI, SQLAlchemy, Alembic, Pydantic, and deterministic engines.

Backend owns:

- project workflow and meal-boundary validation;
- menu persistence, editing, and generation;
- Dish role and meal-type classification validation;
- catalogue-readiness evaluation;
- dish and recipe catalogues;
- transactional product and recipe CSV import;
- purchasing recalculation;
- shopping and packaging persistence;
- equipment requirements, aggregation, overrides, and transactional refresh;
- Russian PDF and Excel generation foundations;
- club branding validation and document snapshots;
- typed system-settings validation, optimistic concurrency, row locking, contrast policy, and safe focused history.

Backend will own authorization, recipe ownership and moderation, working mail delivery, centralized alcohol policy, and the full actor-aware audit log when those deferred phases are implemented.

### Engines

Engines receive prepared data and return deterministic results. Engines do not depend on HTTP, React, or database sessions.

MealPlanService prepares active Dish data, excludes archived recipes, maps persisted role assignments into engine inputs, and invokes the generator in explicit role-aware mode.

## 4. Domain boundaries

### Access — deferred

Invitation-only access and Administrator, Instructor, and Verified Instructor roles are approved target scope, not current implementation. Backend permission enforcement is required when this phase starts.

The `/settings` route is locally accessible until identity exists but is designed to become Administrator-only.

### System Settings — active foundation

ADR-014 defines one settings UI surface with independent typed section ownership:

```text
/settings
  club         -> ClubSettings
  appearance   -> AppearanceSettings
  documents    -> DocumentAppearanceSettings
  modules      -> ModuleSettings
  invitations  -> InvitationSettings
  mail         -> MailSettings

future authenticated user
  preferences  -> UserPreferences
```

`ClubSettings` remains a singleton with `id = 1` and owns only club identity:

- required club name;
- optional profile and contact fields;
- bounded labelled social links;
- main/light/dark logos, square icon, favicon, login background, and document image;
- optimistic version.

`AppearanceSettings` is a separate singleton and owns only organization-wide site appearance:

- complete light and dark color-token sets;
- safe built-in font stack choice;
- comfortable or compact density;
- bounded component radius;
- typed button and card styles;
- shadow enablement;
- preset identity and optimistic version.

Appearance writes are validated and serialized by the backend. Text/surface combinations below the approved contrast threshold are rejected with a human-readable Russian reason. Saved appearance applies globally without application restart. Each browser stores only `system`, `light`, or `dark` preference in localStorage until authenticated `UserPreferences` exists; it does not own organization colors.

Theme-only JSON import/export is versioned, validated before preview, and contains no secrets or club data. It is not the future encrypted full-system configuration archive.

Unrelated settings must not be stored as arbitrary unchecked JSON or generic key/value pairs. Bounded homogeneous value collections may use JSON only inside their owning typed model.

The existing `/api/v1/club-settings` contract remains compatible. The versioned settings page uses `/api/v1/settings/club` and `/api/v1/settings/appearance`. Existing PDF, Excel, print, and ZIP generation continues to consume the main club name/logo branding snapshot until document appearance is implemented.

Focused settings history stores section, local actor label, action, changed field names, resulting version, and timestamp. Club and appearance history exclude binary data, data URLs, complete imported themes, passwords, tokens, and future secrets. This history does not replace the later actor-aware application audit log.

### Projects

Project is the preparation root and stores trip dates, participant count, meal boundaries, status, and links to generated preparation data. `/projects` is the catalogue; `/projects/{id}` is the workspace.

### Nutrition

Owns MealPlan, MealPlanDay, MealSlot, MealSlotDish, Dish, DishMealRole, DishMealRoleMealType, Recipe, RecipeComponent, generation inputs, and recalculation triggers.

MealSlot and MealSlotDish are the primary menu-composition persistence model. MealPlanItem remains a legacy compatibility path.

Dish and Recipe are separate. Current persistence stores one selected `Dish.recipe_id`. Multiple recipe variants, ownership, and preference modes remain future target work.

Dish classification follows ADR-013:

```text
dish_meal_roles
  (dish_id, role) primary key
  is_repeatable

dish_meal_role_meal_types
  (dish_id, role, meal_type) primary key
```

Role compatibility is owned by Dish, not Recipe or MealSlotDish. Manual MealSlotDish assignments remain authoritative.

Automatic composition policy:

- breakfast/lunch/dinner require compatible `main`;
- snack requires compatible `snack`;
- compatible `addition` and `drink` are optional;
- composition order is `main → addition → drink`;
- repeatability belongs to the selected `(dish, role)` assignment;
- non-repeatable main dishes use trip-calendar-day three-day diversity;
- marked manual slots remain authoritative during regeneration;
- unclassified and archived-recipe dishes are not automatic candidates;
- missing required pools produce explicit warnings rather than an incompatible fallback.

### Catalogue import

CSV import has preview and apply operations. Parsing, validation, duplicate handling, references, and transaction boundaries belong to Backend. Invalid input must not create partial catalogue data.

### Shopping

Owns ingredient aggregation, package rounding, purchased quantities, checklist state, comments, responsible-person text, category, and surplus. Participant changes, MealSlot mutations, and Dish recipe replacement refresh affected persisted projections transactionally.

### Equipment

Owns recipe equipment requirements, maximum simultaneous aggregation, persisted project lists, manual rows, calculated/manual quantities, removals, transactional refresh, and Russian export data.

### Documents

Owns Russian PDF, Excel, print, and ZIP generation. Existing purchase/equipment outputs and main club branding are implemented. The approved consolidated document set and independent document-appearance settings remain incomplete.

Each generated package uses one immutable brand/data snapshot so PDF, Excel, print, and ZIP cannot observe different settings during the same generation transaction.

### Audit

A focused safe System Settings history exists without identity and attributes changes to `Локальный администратор`. The full actor-aware application audit log begins after identity and roles exist.

## 5. Recalculation contract

Implemented triggers preserve selected menu structure and recalculate purchasing and equipment data transactionally:

```text
Participant count / MealSlot / Dish.recipe_id
        ↓
Recipe components and legacy ingredients
        ↓
Ingredient totals
        ↓
Packages
        ↓
Purchase list and checklist

Recipe equipment / participant count
        ↓
Maximum simultaneous equipment requirements
        ↓
Persisted equipment list with project overrides
```

Recalculation must be transactional or leave the previous valid state unchanged. Checklist state and valid project overrides are preserved where their underlying records remain.

## 6. Persistence evolution

- Existing working models evolve incrementally.
- Alembic must have exactly one head.
- `main` currently ends at `h10008`; draft PR #85 adds additive `h10009` appearance persistence.
- Applied migrations are not rewritten when real data may exist.
- Public API placeholders are prohibited.
- Legacy compatibility requires a verified consumer or migration plan.
- One-recipe-per-Dish persistence must not be described as multi-variant until a migration and selection contract exist.
- Role or meal-type metadata must never be inferred from names, ingredients, recipes, or historical placement.
- Settings domains require typed ownership, validation, migration, concurrency, and secret-boundary decisions.

## 7. Security rules

- Club data is not transmitted to external paid services.
- Multi-user permissions must be enforced in Backend when introduced.
- The settings page becomes Administrator-only after access foundation.
- SVG, arbitrary custom CSS, uploaded fonts, and remote font URLs are not accepted in the current settings model.
- Settings images are validated by MIME type, decoded content, dimensions, and size.
- Theme imports are schema-versioned and fully validated before entering preview state.
- Mail passwords and similar credentials use external or write-only secret handling.
- Secrets never appear in normal API responses, logs, focused history, diagnostics, theme-only exports, or unencrypted configuration exports.
- Alcohol prohibition remains approved product scope but still needs centralized API and import enforcement.

## 8. Future domains

Not part of the current implemented scope:

- participant profiles and personal data;
- routes and GPX;
- logistics and load distribution;
- warehouse balances and issue workflow;
- price aggregator integration;
- multi-tenant support.

## 9. Change rule

Any change to deployment boundaries, domain ownership, persistence strategy, stack, or MVP scope requires:

1. Product Owner approval when product or stack is affected;
2. an ADR;
3. synchronized documentation;
4. migration and compatibility analysis;
5. tests.

See ADR-012, ADR-013, ADR-014, and `PRODUCT_SPEC.md`.
