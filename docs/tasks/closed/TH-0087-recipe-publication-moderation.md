# TH-0087 — Recipe Publication and Moderation

Status: DONE

Completed: 2026-07-18

## Goal

Add the first complete personal-recipe publication workflow on top of TH-0086 ownership: an owner submits a personal recipe, a permitted reviewer publishes it to the club library or rejects it with a comment, and the owner may correct and resubmit a rejected recipe.

## Delivered

### Persistence

- added lifecycle states `draft`, `submitted`, `rejected`, and `published`;
- migrated existing CLUB recipes to `published` through Alembic `h10018`;
- new PERSONAL recipes start in `draft`;
- persisted submitter, submission time, reviewer, review time, and latest rejection comment;
- preserved submitter attribution when a recipe becomes CLUB;
- kept exactly one Alembic head.

### Backend

- owners may submit active PERSONAL `draft` and `rejected` recipes;
- `submitted` recipes are locked against ordinary root, component, note, equipment, and archive changes;
- Administrator and Verified Instructor have a separate moderation queue;
- Verified Instructor may review only another user's submission;
- Administrator may review any submitted recipe;
- publication converts PERSONAL to CLUB, clears current owner, and preserves submitter attribution;
- rejection requires a normalized non-empty comment;
- rejected recipes return to the owner for editing and resubmission;
- resubmission clears the previous decision;
- submit, publish, and reject transitions use a database row lock;
- API responses expose lifecycle metadata and current-actor capabilities.

### Frontend and acceptance

- library and moderation views are responsive;
- lifecycle, submitter, reviewer, and rejection feedback are visible;
- submit, publish, reject, archive, restore, edit, and delete controls use Backend capabilities;
- rejection uses a required-comment dialog;
- focused Chrome acceptance opens the moderation queue, reviews a submitted recipe, rejects it with a comment, verifies the API payload, and checks mobile overflow;
- API tests cover Instructor, Verified Instructor, Administrator, self-review prevention, submitted locks, rejection/resubmission, and publication attribution.

## Scope intentionally deferred

- multiple Recipe variants per Dish;
- club/personal generation modes;
- immutable moderation history beyond the latest decision;
- moderation notifications;
- actor-aware audit;
- project ACLs, multi-tenancy, and live collaboration.

## Verification

Implementation head `7dd0ddd398b4f4b82d43f30db8c95c0489f2f31b` passed:

- Quality #887;
- Document Quality #502;
- Guided Release Acceptance #453;
- Operator Docs #439;
- Docker Release Runtime #434.

The pull request receives one final exact-head run after task and roadmap closure before squash merge.
