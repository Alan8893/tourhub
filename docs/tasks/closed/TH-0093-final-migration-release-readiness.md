# TH-0093 — Final Migration and Release Readiness

Status: CLOSED

Closed: 2026-07-19

Release tag: `v0.1.0`

Alembic head: `h10021`

## Goal

Prove that the accepted feature-frozen first release can complete its final PostgreSQL migration cycle and production-like deployment checks, then create the release tag only from one green exact merged `main` head.

## Delivered

- added a machine-readable release-readiness manifest bound to Backend version `0.1.0` and tag `v0.1.0`;
- added a versioned production deployment checklist covering prerequisites, configuration, secrets, backup, upgrade, health, LAN access, product smoke, rollback, and operator sign-off;
- added first-release notes with accepted scope and deferred non-blocking capabilities;
- added release-readiness validation for Product Acceptance state, migration boundary, tag/version consistency, required workflows, checklist, release notes, task state, and local-only runtime services;
- added a real PostgreSQL 18 cycle for `h10020 → h10021 → h10020 → h10021`;
- seeded allowed, prohibited, manually archived, non-default variant, and historically assigned catalogue data against the real `h10020` schema;
- verified policy archive markers, active catalogue filtering, manual archive preservation, historical Recipe/Dish relationships, downgrade restoration semantics, one Alembic head, and final revision `h10021`;
- added machine-readable migration evidence uploaded on both success and failure;
- added `push: main` evidence for Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, and Docker Release Runtime;
- added an exact-head finalizer that refuses missing, pending, skipped, cancelled, or failed workflows and creates lightweight tag `v0.1.0` only on the verified merged SHA;
- preserved the feature-frozen product scope without adding a migration, capability, external service, architecture change, multi-tenancy, or microservice boundary.

## Verification

The release-candidate PR head passed:

- release contract compilation and Ruff;
- release-readiness manifest validation;
- release Compose syntax validation;
- PostgreSQL 18 `h10020 → h10021 → h10020 → h10021` with representative persisted data;
- Product Acceptance;
- Quality, including full Backend/Frontend, Alembic single head, and PostgreSQL backup/restore;
- Document Quality;
- Guided Release Acceptance;
- Operator Docs;
- Docker Release Runtime.

The final tag job runs only after squash-merge. It waits for the same six required workflows to pass as `push` runs on the exact merged `main` SHA, then creates `v0.1.0`. If that invariant is not satisfied, no tag is created and the release is not complete.

## Rollback boundary

Production rollback is backup-based:

1. retain the pre-upgrade custom-format PostgreSQL dump;
2. stop application services;
3. restore the dump with the documented explicit confirmation command;
4. run the code/tag matching the restored database revision;
5. repeat revision, health, LAN, authentication, Project reload, and document smoke checks.

`alembic downgrade` is release verification evidence, not the normal production rollback mechanism.

## Definition of done

- [x] PostgreSQL 18 passes `h10020 → h10021 → h10020 → h10021` with representative data and final revision `h10021`.
- [x] Alembic has exactly one head.
- [x] The deployment checklist is versioned, executable, and verified against the release stack.
- [x] Product Acceptance remains `feature_frozen` and green.
- [x] Required PR workflows pass on one exact candidate head.
- [x] Final release-readiness evidence is machine-readable and human-readable.
- [x] Tag creation is restricted to the exact merged `main` head after all required push workflows pass.
- [x] Current documentation records release readiness and the backup-based rollback boundary.
- [x] No release-blocking product debt remains.

## Result

TourHub v0.1.0 is release-ready at Alembic `h10021`. The merge-triggered Final Release Readiness workflow owns the final exact-head evidence and tag creation. Post-release work must remain a separate task and cannot silently expand the accepted first-release scope.
