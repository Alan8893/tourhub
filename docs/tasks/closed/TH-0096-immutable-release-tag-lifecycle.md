# TH-0096 — Immutable Release Tag Lifecycle

Status: DONE

Completed: 2026-07-19

## Goal

Allow post-release commits to pass Final Release Readiness without moving, recreating, or invalidating the already published `v0.1.0` tag.

## Reproducible defect

TH-0093 intentionally ran Final Release Readiness on every push to `main`. Its tag job always used the current push SHA as the expected `v0.1.0` target. After `v0.1.0` was published, any later post-release merge would therefore fail because the immutable tag correctly remained on the original release commit. Moving the tag would corrupt the released evidence.

The defect was discovered before merging TH-0095.

## Delivered fix

- Release readiness manifest state changes from `release_ready` to `released`.
- The manifest records the immutable release commit:
  - tag: `v0.1.0`;
  - commit: `8bcc2d2d9414d812d81634330034b15121c8442f`.
- `validate_release_readiness.py` accepts the published lifecycle only with a lowercase 40-character `release_commit_sha` and closed TH-0093.
- `finalize_release.py` keeps two explicit policies:
  - `release_ready`: current exact head may create the not-yet-published tag;
  - `released`: current exact head workflows are validated, but the existing tag must remain on the recorded release commit and cannot be created or moved.
- Missing or moved published tags fail Final Release Readiness.
- Unit tests cover candidate tag creation, immutable verification, missing tag failure, moved tag failure, and lifecycle policy selection.
- Release notes record the published tag and immutable commit.

## Non-goals

- no tag movement;
- no new release version;
- no product, Backend, Frontend, database, migration, runtime, or architecture change;
- no weakening of exact-head workflow checks for current `main` commits;
- no modification of v0.1.0 contents.

## Acceptance

- manifest validation succeeds in `released` state;
- release lifecycle unit tests succeed;
- Final Release Readiness contract and PostgreSQL cycle succeed on the PR;
- after merge, all required exact-head push workflows succeed;
- the final tag job verifies that `v0.1.0` still points to `8bcc2d2d9414d812d81634330034b15121c8442f`;
- tag comparison remains identical to the recorded release commit.
