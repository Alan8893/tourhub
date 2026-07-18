# TH-0086 — Recipe Ownership Foundation

Status: DONE

Completed: 2026-07-18

## Goal

Introduce explicit CLUB/PERSONAL recipe ownership and enforce the first role-aware recipe editing boundary before publication and moderation are added.

## Delivered

### Persistence

- Recipe `scope` supports `club` and `personal`;
- nullable `owner_user_id` references User;
- database constraints require CLUB without an owner and PERSONAL with one owner;
- migration `h10017` preserves every existing recipe as CLUB;
- archive state remains independent of ownership.

### Backend

- interactive creation produces a PERSONAL recipe owned by the authenticated user;
- trusted internal catalogue/import creation remains CLUB;
- Administrator sees all recipes; other roles see CLUB plus their own PERSONAL recipes;
- unrelated PERSONAL recipes are hidden as not found;
- Instructor edits owned PERSONAL recipes only;
- Verified Instructor edits owned PERSONAL and CLUB recipes;
- Administrator edits all recipes and remains the only permanent-delete role;
- usage guards still prevent deletion of recipes assigned to a Dish;
- root, component, note, and equipment mutations share one ownership policy;
- list, detail, and write responses project safe owner identity and actor capabilities.

### Frontend

- the recipe library labels CLUB and PERSONAL recipes;
- safe owner names are shown where available;
- new recipes are explicitly described as personal;
- read-only recipes hide mutation actions;
- archive, components, and notes follow server-projected capabilities;
- responsive production build and browser acceptance remain green.

## Deferred

- submission, review queue, publication, rejection, resubmission, and moderation history;
- PERSONAL-to-CLUB publication transition;
- multiple Recipe variants per Dish;
- club/personal generation modes;
- actor-aware audit;
- project ACLs, multi-tenancy, and live collaboration.

## Validation

Implementation head `29b84be3f98a721d8d0faf2fa1908f65681820cd` passed:

- Quality #858;
- Document Quality #474;
- Guided Release Acceptance #425;
- Operator Docs #411;
- Docker Release Runtime #406.

The migration keeps one Alembic head at `h10017` and the clean PostgreSQL 18 release stack applies it successfully.