# ADR-021 — Recipe Publication and Moderation

Status: Accepted

Date: 2026-07-18

## Context

TH-0086 introduced explicit CLUB/PERSONAL ownership and role-aware editing, but personal recipes cannot yet enter the shared club library. The approved product scope requires Instructor submission, Verified Instructor review, publication, archive, and rejection with a comment. The workflow must not weaken personal-recipe privacy or allow a submitted recipe to change underneath a reviewer.

## Decision

### Lifecycle

Recipe owns one current lifecycle state:

```text
draft
  → submitted
      → published
      → rejected
rejected
  → submitted
```

- existing CLUB recipes migrate to `published`;
- every new interactive PERSONAL recipe starts as `draft`;
- `published` recipes are CLUB and have no current owner;
- `draft`, `submitted`, and `rejected` recipes are PERSONAL and retain one owner;
- archive remains an orthogonal retention state and is not a publication state.

### Attribution and decision metadata

Recipe stores:

- `submitted_by_user_id` and `submitted_at` for the latest submission;
- `reviewed_by_user_id` and `reviewed_at` for the latest decision;
- `review_comment` only for the latest rejection.

Publishing clears `owner_user_id` when scope becomes CLUB but preserves `submitted_by_user_id`, so the contributor is not lost. Resubmission refreshes submission metadata and clears the previous review decision.

### Authorization

- the owner may submit an active PERSONAL recipe in `draft` or `rejected`;
- the owner may edit `draft` and `rejected`, but not `submitted`;
- Administrator may review any submitted recipe;
- Verified Instructor may review a submitted recipe only when another user owns it;
- Instructor cannot open the moderation queue;
- publication and rejection require the recipe to still be PERSONAL and `submitted`;
- rejection requires a non-empty comment;
- normal CLUB editing remains available to Administrator and Verified Instructor after publication.

Backend returns explicit capabilities for presentation. Frontend role checks may hide the moderation entry point, but Backend remains authoritative.

### Concurrency

Submit, publish, and reject load the Recipe row with `SELECT ... FOR UPDATE`, validate the current state after locking, mutate, and commit in one transaction. A second concurrent decision sees the completed state and is rejected rather than overwriting the first decision.

### Visibility

The normal library lists CLUB recipes plus the current user's PERSONAL recipes; Administrator may continue to list all. A separate moderation view returns active submitted PERSONAL recipes to authorized reviewers. A reviewer may open a submitted recipe directly, while unrelated drafts and rejections remain hidden.

## Consequences

- personal work remains private until submission;
- reviewers receive a stable submitted snapshot because owner editing is blocked;
- a published recipe becomes a shared club standard without losing submitter attribution;
- the latest rejection reason is visible to the owner and is cleared on resubmission;
- a full decision history and actor-aware audit remain separate future capabilities;
- Dish variants, generation modes, and moderation notifications remain outside this slice.
