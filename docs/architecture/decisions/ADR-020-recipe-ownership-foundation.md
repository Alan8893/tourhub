# ADR-020 — Recipe Ownership Foundation

Status: Accepted

Date: 2026-07-18

## Context

TourHub now has invitation-only accounts and three approved roles, but Recipe remains a global record with no owner or club/personal distinction. The product specification requires CLUB standards and PERSONAL instructor recipes, followed later by submission, review, publication, rejection, archive, and recipe-selection modes.

Ownership must be introduced before moderation so later lifecycle transitions have an unambiguous source identity. The first slice must preserve existing recipe, Dish, shopping, import, and equipment behavior while preventing one Instructor from modifying another user's personal work.

## Decision

### Persistence

Recipe gains:

- `scope`: `club` or `personal`;
- nullable `owner_user_id` referencing User.

The database enforces exactly one valid ownership shape:

- CLUB: `owner_user_id IS NULL`;
- PERSONAL: `owner_user_id IS NOT NULL`.

Archive remains an independent boolean lifecycle flag. Existing recipes are migrated to CLUB with no owner because they already form the shared catalogue used by dishes and generated preparation data.

### Creation

Every interactive API recipe creation creates a PERSONAL recipe owned by the authenticated actor. Direct creation of CLUB recipes is not exposed in this slice. A later accepted publication transition will convert an eligible PERSONAL recipe into a CLUB recipe.

Trusted internal catalogue/import services may continue to create or access recipes without an interactive actor. Interactive routers must always provide the authenticated actor to ownership-aware services.

### Visibility

- Administrator may view CLUB and all PERSONAL recipes.
- Instructor and Verified Instructor may view CLUB recipes and their own PERSONAL recipes.
- Other users' personal drafts are not exposed before a submission lifecycle exists.

A hidden recipe is returned as not found rather than revealing its existence.

### Editing

- Administrator may edit any visible recipe.
- Verified Instructor may edit CLUB recipes and owned PERSONAL recipes.
- Instructor may edit only owned PERSONAL recipes.
- Archived recipes remain non-editable through component, note, and equipment mutation paths.
- Permanent deletion remains Administrator-only and retains existing usage guards.

The same policy applies to the recipe root and all owned child records so ownership cannot be bypassed through a nested endpoint.

### API projection

Recipe list, detail, and write responses include:

- scope;
- safe owner id and display name where present;
- `is_owned_by_current_user`;
- `can_edit`;
- `can_delete`.

Frontend controls are guidance only. Backend services remain the authority.

## Consequences

- existing shared recipes remain available without manual reassignment;
- newly created recipes are attributable to a real user;
- instructors cannot edit another instructor's personal recipe;
- verified instructors gain the approved distinction for editing club standards without gaining access to unrelated personal drafts;
- publication and moderation can be implemented as explicit transitions in a later task;
- Dish variants, generation modes, and actor-aware audit remain separate capabilities.