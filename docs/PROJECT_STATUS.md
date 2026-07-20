# TourHub Project Status

Status date: 2026-07-20

## Current phase

TourHub v0.1.0 is release-ready at Alembic head `h10021`.

The feature-frozen first release is complete through TH-0093. Post-release work delivered routed Project UX (TH-0095), Product editing (TH-0097), published Recipe-to-Dish synchronization (TH-0098), Project audit coverage (TH-0099), menu/MealSlot audit coverage (TH-0100), System Settings/mail audit coverage (TH-0101), and invitation lifecycle/delivery-result audit coverage (TH-0102).

## Verified baseline

- PostgreSQL 18 migration cycle and one Alembic head ending at `h10021`;
- immutable release tag `v0.1.0` at its recorded release SHA;
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness on pull requests and `main`;
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only;
- no TH-0102 migration, architecture, runtime, invitation-validity, delivery-order, or product-scope change.

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
- typed System Settings changes and Administrator mail-operation outcomes through TH-0101;
- invitation create, reissue, revoke, and accept transitions append semantic events in their owning transactions through TH-0102;
- create, reissue, and revoke snapshot the authenticated Administrator; acceptance snapshots the newly created User as actor;
- automatic invitation delivery records only safe status, attempt count, recipient domain, operation kind, and role after the lifecycle commit;
- a delivery failure or delivery-audit persistence failure never invalidates the invitation or removes the one-time manual link;
- raw invitation tokens, acceptance links, passwords, password hashes, raw sessions, session hashes, SMTP secrets, provider messages, protocol transcripts, exception details, and arbitrary request bodies are excluded;
- Administrator Audit UI/API expose Russian User, Recipe, Project, Menu, MealSlot, System Settings, Mail, and Invitation labels and filters.

## TH-0102 evidence

Candidate implementation head `dab3e071a13d131b5dc2a7d890923faeffe2c55c` passed strict Ruff/mypy, the full Backend test suite, Frontend tests/build/browser acceptance, Product Acceptance, PostgreSQL backup/restore, Alembic single-head validation, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness.

The final documentation-only head is verified again before merge.

## Deferred non-blocking debt

- semantic audit coverage for catalogue/import, shopping, equipment, and document-generation writes;
- audit export, retention UI, SIEM, undo, and replay;
- ownership-aware import UX and Product/Dish archive-management UI;
- moderation notifications, account recovery, session administration, asynchronous mail, and bounce handling;
- richer Recipe metadata, per-meal switching, and preference weights;
- participant profiles, routes/GPX, warehouse and procurement domains;
- scheduled/emailed documents, signatures, and encrypted configuration archives.

## Next work

TH-0102 is complete. No later task is selected automatically. Catalogue/import, shopping, equipment, and document-generation writes are the first remaining explicit audit-coverage cluster and require another Product Owner decision.
