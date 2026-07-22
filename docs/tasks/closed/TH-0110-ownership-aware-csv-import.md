# TH-0110 — Ownership-Aware CSV Import

Status: DONE

## Goal

Make Recipe CSV import respect the delivered CLUB/PERSONAL ownership model without changing the Product CSV contract or weakening preview/apply safety.

## Delivered product contract

- Product CSV import remains club-wide and its existing API/CSV format is unchanged.
- Recipe import UI requires one explicit target scope for the whole operation: `CLUB` or `PERSONAL`.
- `PERSONAL` imports are owned by the authenticated user and are created as personal drafts.
- `CLUB` imports are created as published club Recipes and remain preparation-authorized.
- Recipe preview returns an actor/content/scope-bound fingerprint; ownership-aware apply must return the matching token.
- Changing CSV content or ownership scope invalidates preview and apply returns HTTP 409 without writes or audit.
- Existing legacy Recipe apply calls without the new fields remain compatible and resolve to CLUB import after full server validation.
- Components and notes inherit the Recipe identity and introduce no independent ownership.
- Duplicate/reference validation, central alcohol policy, row/field errors, and all-or-nothing transaction behavior remain mandatory.
- Successful apply keeps actor-aware bounded `catalog_import_applied` audit and excludes source CSV bodies.

## Backend

- extended import request/result schemas with optional Recipe ownership scope and preview token;
- added `OwnershipAwareCatalogImportService` around the existing parser and alcohol-aware validation;
- explicit PERSONAL creation persists `scope=personal`, current `owner_user_id`, and `lifecycle_status=draft`;
- explicit CLUB creation persists `scope=club`, no owner, and `lifecycle_status=published`;
- preview/apply mismatch is rejected before persistence;
- Product import continues through the established service unchanged;
- route authorization remains centralized through `require_preparation_access`;
- state and audit commit or roll back together.

## Frontend

- Recipe CSV workflow contains a responsive ownership selector and clear CLUB/PERSONAL outcome explanation;
- preview and confirmation show the selected ownership target;
- apply uses the Backend-issued preview token;
- content, kind, or ownership changes reset preview;
- upload, paste, template download, validation, loading, error, and success states remain available;
- Product import UI remains unchanged apart from shared result typing.

## Verification

- Backend tests cover explicit CLUB and PERSONAL creation, legacy compatibility, Product-field rejection, scope/content mismatch, correct catalogue projection, and forced-audit rollback;
- Frontend tests cover request construction, token/scope matching, and user-facing ownership descriptions;
- real-Chrome acceptance covers PERSONAL preview/apply payloads, token propagation, scope-change invalidation, and mobile overflow;
- Product Acceptance and the full Quality browser suite remain required on the exact final head;
- no migration was required and Alembic remains one head at `h10023`;
- immutable tag `v0.1.0` remains unchanged.

## Non-goals retained

- per-row mixed ownership;
- ownership changes for existing Recipes;
- Product ownership or personal Product catalogues;
- automatic moderation/publication of personal imports;
- bulk import of Projects, Dishes, users, or teams;
- Project copy, audit retention, session cleanup, or notification delivery.
