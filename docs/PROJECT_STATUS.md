# TourHub Project Status

Status date: 2026-07-18

## Current phase

The guided single-club preparation baseline, production-like runtime, Product Completeness Audit, complete System Settings foundation, first-release Access foundation, working SMTP delivery, multi-user operational readiness, and Recipe Ownership Foundation are complete through PR #96. Draft PR #97 implements recipe publication and moderation as TH-0087.

## Verified baseline

- Merged Alembic head: `h10017`.
- Active draft Alembic head: `h10018`.
- PR #84 through PR #89 delivered the typed System Settings foundation (`h10008`–`h10013`).
- PR #90 merged as `26c4d4eb9246de44579451fe3d6e7bd631538324` (`h10014`).
- PR #91 merged as `2348870864efa1da20547c1a6564dc5f9b6488ef` (`h10015`).
- PR #92 merged as `257d82a9f4f7e47095f8e96635bf62a9ed14e722` (`h10016`).
- PR #93 merged as `21a66a2caae4e52f8e1a87bd242666703c4bc296` with no migration.
- PR #94 merged as `3c51d4c1d0bb0bd96d23a1f4ace0947ae48e9101` with no migration.
- PR #95 merged as `82315e0ff9520b52ae5244f69bc05d4a5d0db5b3`.
- PR #96 merged as `d9ee573d44d885b48a2ce9424e9695f25d95a665`; exact implementation head `17b76c6933b69831c761ad3157b557cce2d0a9b7` passed Quality #868, Document Quality #484, Guided Release Acceptance #435, Operator Docs #421, and Docker Release Runtime #416.
- MealSlot and MealSlotDish remain primary; MealPlanItem remains compatibility-only.

## Implemented baseline

- complete guided preparation through Russian purchase/equipment documents and ZIP;
- persisted shopping, packaging, checklist, equipment, overrides, recalculation, and reload-safe readiness;
- installation, update, backup, restore, recovery, release images, health checks, API proxy, and restart persistence;
- responsive typed System Settings through ADR-014;
- invitation-only Access, explicit roles, user administration, and preparation authorization through ADR-015–ADR-018;
- working SMTP delivery and invitation fallback through ADR-019;
- multiple independent sessions, current-role propagation, complete deactivation revocation, centralized frontend 401 handling, exact route return, and visible current role through TH-0085;
- Recipe CLUB/PERSONAL ownership, owner identity, role-aware visibility/editing, nested-operation enforcement, and responsive ownership UI through ADR-020 and `h10017`.

## Active recipe publication slice

Draft PR #97 adds ADR-021 and `h10018`:

- lifecycle states `draft`, `submitted`, `rejected`, and `published`;
- existing CLUB recipes remain published;
- new PERSONAL recipes start as editable drafts;
- the owner may submit a draft or rejected recipe;
- submitted recipes are locked against normal editing and archive operations;
- Administrator and Verified Instructor receive a separate moderation queue;
- Verified Instructor cannot review their own submission;
- publication converts PERSONAL to CLUB while retaining submitter attribution;
- rejection requires a comment visible to the owner;
- resubmission clears the previous decision and refreshes submission metadata;
- lifecycle transitions use PostgreSQL row locking and Backend-projected capabilities.

## Remaining sequence

1. Dish recipe variants and club/personal generation modes.
2. Central alcohol policy.
3. Actor-aware identity and consolidated audit, including full moderation history.
4. Consolidated exports, product acceptance, then feature freeze.

## Quality debt

- active catalogue/import acceptance;
- ownership-aware import UX beyond trusted CLUB catalogue imports;
- full moderation history beyond the latest decision;
- moderation notifications remain deferred;
- session administration and account recovery remain deferred Access operations;
- asynchronous delivery queues and bounce handling remain deferred;
- final PostgreSQL migration cycle after feature freeze;
- final release workflow and deployment checklist.
