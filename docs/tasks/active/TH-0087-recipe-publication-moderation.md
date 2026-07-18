# TH-0087 — Recipe Publication and Moderation

Status: IN PROGRESS

Last updated: 2026-07-18

## Goal

Add the first complete personal-recipe publication workflow on top of TH-0086 ownership: an owner submits a personal recipe, a permitted reviewer publishes it to the club library or rejects it with a comment, and the owner may correct and resubmit a rejected recipe.

## Scope

### Persistence

- add recipe lifecycle states `draft`, `submitted`, `rejected`, and `published`;
- migrate all existing CLUB recipes to `published`;
- keep new PERSONAL recipes in `draft`;
- persist submitter, submission time, reviewer, review time, and the latest rejection comment;
- preserve submitter attribution when a recipe becomes CLUB;
- advance Alembic from `h10017` to `h10018` with one head.

### Backend

- allow the owner of an active PERSONAL `draft` or `rejected` recipe to submit it;
- lock `submitted` recipes against ordinary editing and archiving;
- expose a moderation queue to Administrator and Verified Instructor;
- allow Verified Instructor to review recipes submitted by other users;
- allow Administrator to review any submitted recipe;
- publish by converting PERSONAL to CLUB, clearing owner, and preserving submitter attribution;
- reject only with a non-empty operator-safe comment;
- allow rejected recipes to be edited by the owner and submitted again;
- serialize lifecycle transitions with a database row lock;
- expose lifecycle metadata and current-actor capabilities in list/detail/write responses.

### Frontend

- show lifecycle state, submitter, reviewer, and rejection comment;
- add a moderation view for Administrator and Verified Instructor;
- add submit, publish, and reject actions based only on API capabilities;
- require a rejection comment in a responsive dialog;
- keep archived, ownership, component, note, and equipment flows compatible.

## Out of scope

- multiple Recipe variants per Dish;
- generation modes using personal recipes;
- moderation history beyond the latest decision;
- notifications or mail for moderation events;
- actor-aware audit log;
- per-project ownership, ACLs, multi-tenancy, or live collaboration.

## Definition of done

- migration and constraints preserve existing CLUB recipes as published;
- every lifecycle transition is authorized and serialized;
- unrelated personal drafts and rejections remain hidden;
- submitted recipes are visible in the moderation queue and cannot be edited by their owner;
- rejection requires a comment and resubmission clears the previous decision;
- publication creates a shared CLUB recipe while retaining submitter attribution;
- Backend tests cover Instructor, Verified Instructor, and Administrator paths;
- frontend presentation and actions reflect Backend capabilities;
- current domain, architecture, roadmap, status, technical debt, task index, and ADR are synchronized;
- exact-head repository quality gates pass.
