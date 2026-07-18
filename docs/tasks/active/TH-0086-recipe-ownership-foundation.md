# TH-0086 — Recipe Ownership Foundation

Status: IN PROGRESS

Last updated: 2026-07-18

## Goal

Introduce explicit CLUB/PERSONAL recipe ownership and enforce the first role-aware recipe editing boundary before publication and moderation are added.

## Scope

### Persistence

- add `scope` to Recipe with supported values `club` and `personal`;
- add nullable `owner_user_id` referencing User;
- require CLUB recipes to have no owner and PERSONAL recipes to have one owner;
- migrate every existing recipe deterministically to CLUB with no owner;
- keep archived state separate from scope;
- advance Alembic from `h10016` to `h10017` with one head.

### Backend

- create every browser/API recipe as PERSONAL and owned by the current authenticated user;
- list CLUB recipes plus the current user's PERSONAL recipes; Administrator may list all PERSONAL recipes;
- return scope, safe owner identity, and current-actor capabilities in recipe list/detail/write responses;
- allow Instructor to edit only owned PERSONAL recipes;
- allow Verified Instructor to edit owned PERSONAL recipes and CLUB recipes;
- allow Administrator to edit all recipes;
- allow permanent deletion only to Administrator and only when existing usage guards permit it;
- apply the same edit policy to recipe components, notes, and equipment requirements;
- retain trusted internal service use for catalogue/import paths that do not run as an interactive user.

### Frontend

- show whether a recipe is club or personal and display its safe owner label;
- explain that newly created recipes are personal;
- hide or disable mutation actions when the API reports that the current user cannot edit or delete;
- keep archive and existing catalogue flows responsive.

## Out of scope

- submission, review queue, publication, rejection comments, or moderation history;
- converting PERSONAL recipes to CLUB;
- multiple recipe variants per Dish;
- generation modes using personal recipes;
- actor-aware audit records;
- per-project ownership, ACLs, multi-tenancy, or live collaborative editing.

## Definition of done

- migration and constraints preserve all existing recipes as CLUB;
- ownership cannot be bypassed through component, note, or equipment endpoints;
- focused Backend and browser/API tests cover all three roles;
- current domain, architecture, roadmap, status, technical debt, task index, and ADR are synchronized;
- exact-head repository quality gates pass.