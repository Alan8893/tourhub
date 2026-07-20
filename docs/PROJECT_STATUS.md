# TourHub Project Status

Status date: 2026-07-20

## Current phase

TourHub v0.1.0 is release-ready at Alembic head `h10021`.

The feature-frozen first release is complete through TH-0093. Post-release work delivered routed Project UX (TH-0095), Product editing (TH-0097), published Recipe-to-Dish synchronization (TH-0098), Project audit coverage (TH-0099), menu/MealSlot audit coverage (TH-0100), and System Settings/mail audit coverage (TH-0101).

## Verified baseline

- PostgreSQL 18 migration cycle and one Alembic head ending at `h10021`;
- immutable release tag `v0.1.0` at its recorded release SHA;
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness on pull requests and `main`;
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only;
- no TH-0101 migration, architecture, runtime, mail-delivery, invitation-lifecycle, or product-scope change.

## Delivered post-release improvements

### Project workspace and catalogue workflow

- compact routed Project work areas and responsive navigation through TH-0095;
- shared Product editing without changing Product IDs, Recipe relationships, or RecipeComponent values through TH-0097;
- transaction-owned published Recipe-to-Dish synchronization with explicit human-owned generator readiness through TH-0098.

### Actor-aware audit

- append-only AuditEvent persistence and safe actor snapshots through `h10020`;
- user-access and Recipe moderation actions in owning transactions;
- Project creation, participant recalculation, generation-mode updates, and preparation orchestration through TH-0099;
- menu generation/regeneration and manual MealSlot add/remove/replace in owning transactions through TH-0100;
- Club, Appearance, Document Appearance, Module, Invitation Policy, and Mail Settings changes record semantic events only when persisted values change through TH-0101;
- SMTP connection checks and test-message operations record safe `sent`, `failed`, or `unavailable` outcomes with attempts and optional recipient, without SMTP credentials, transcripts, or exception details;
- settings changes, focused history, and AuditEvent share the existing settings commit/rollback boundary;
- image audit stores only configured state, MIME type, and byte size; recursive normalization continues to remove credential, password, token, session, authorization, and secret keys;
- Administrator Audit UI/API expose Russian User, Recipe, Project, Menu, MealSlot, System Settings, and Mail labels and filters.

## TH-0101 evidence

Candidate implementation head `b645bd3e90302c99dc3e64c29bde23ad58b79a29` passed strict Ruff/mypy, the full Backend test suite, Frontend tests/build/browser acceptance, Product Acceptance, PostgreSQL backup/restore, Alembic single-head validation, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness.

The final documentation-only head is verified again before merge.

## Deferred non-blocking debt

- semantic audit coverage for invitation lifecycle/delivery results, catalogue/import, shopping, equipment, and document-generation writes;
- audit export, retention UI, SIEM, undo, and replay;
- ownership-aware import UX and Product/Dish archive-management UI;
- moderation notifications, account recovery, session administration, asynchronous mail, and bounce handling;
- richer Recipe metadata, per-meal switching, and preference weights;
- participant profiles, routes/GPX, warehouse and procurement domains;
- scheduled/emailed documents, signatures, and encrypted configuration archives.

## Next work

TH-0101 is complete. No later task is selected automatically. Invitation lifecycle and delivery-result audit are the first listed unresolved audit slice and require another explicit Product Owner decision.
