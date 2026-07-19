# TourHub Tasks Index

This file contains task status and links. Detailed task descriptions are stored in separate files.

## Active

| ID | Task | Status | Details |
|---|---|---|---|
| TH-0061.5 | Meal Composition Rules Engine | OPERATIONAL MAINTENANCE | ./active/TH-0061.5-menu-rules.md |
| TH-0094 | Project and Menu Audit Instrumentation | IN PROGRESS | ./active/TH-0094-project-menu-audit-instrumentation.md |

TH-0094 is the first post-release debt-reduction slice. It implements already-approved Product Spec audit coverage without changing the released v0.1.0 workflow or feature boundary.

## First-release sequence

| Order | Capability | Gate |
|---|---|---|
| 1 | System Settings foundation | Dedicated page, branding continuity, appearance, typed module settings, invitation/mail configuration boundaries |
| 2 | Access and mail foundation | Bootstrap Administrator, sessions, functional invitations, users, roles, guarded routes, Backend authorization, working SMTP delivery |
| 3 | Multi-user operational readiness | Multiple sessions, immediate role propagation, revoked-session handling, exact route return, visible current role |
| 4 | Recipe ownership and lifecycle | CLUB/PERSONAL ownership, variants, publication, moderation, generation modes |
| 5 | Actor-aware audit | Safe actor-attributed history foundation and explicit domain coverage |
| 6 | Consolidated export completeness | Approved Russian PDF and workbook contents using one brand snapshot |
| 7 | Central alcohol prohibition | Shared API/import policy and existing-record handling immediately before acceptance |
| 8 | Product acceptance and feature freeze | End-to-end acceptance, explicit optional-scope decisions, and frozen first-release capability scope |
| 9 | Final release readiness | PostgreSQL migration cycle, deployment checklist, exact-head final workflow, and release tag |

The complete first-release sequence is delivered through TH-0093 and tagged `v0.1.0`. Post-release work remains independently scoped and must not modify that tag.

## Completed

| ID | Task | Status |
|---|---|---|
| TH-0053 | PDF Generator Refactoring | DONE |
| TH-0060 | MVP Workflow Slice | DONE |
| TH-0061 | User Project Preparation Wizard | DONE |
| TH-0061.3 | MealPlan Domain Expansion | DONE |
| TH-0061.4 | Meal Composition Model | DONE |
| TH-0061.6 | Recipe Components and Recipe Variants | DONE |
| TH-0061.7 | Recipe Components Implementation | DONE |
| TH-0063 | MealSlot Integration | DONE |
| TH-0064 | Project Stabilization and Documentation Recovery | DONE |
| TH-0065 | Meal Plan Editor UX | DONE |
| TH-0066 | Project Catalogue | DONE |
| TH-0067 | Dish Catalogue and Recipe Assignment | DONE |
| TH-0068 | Catalogue CSV Import | DONE |
| TH-0069 | Dish Recipe Purchasing Recalculation | DONE |
| TH-0070 | Critical Meal Plan Stabilization | DONE |
| TH-0071 | Operator Installation and Update Runbook | DONE |
| TH-0072 | Docker Release Runtime Validation | DONE |
| TH-0073 | Product Completeness Audit | DONE |
| TH-0074 | System Settings Club Foundation | DONE |
| TH-0075 | System Settings Appearance | DONE |
| TH-0076 | System Settings Document Appearance | DONE |
| TH-0077 | System Settings Module Visibility | DONE |
| TH-0078 | System Settings Invitation Policy | DONE |
| TH-0079 | System Settings Mail Boundary | DONE |
| TH-0080 | Access Bootstrap and Authentication | DONE |
| TH-0081 | Functional Invitation Lifecycle | DONE |
| TH-0082 | User Administration and Roles | DONE |
| TH-0083 | Preparation Authorization Matrix | DONE |
| TH-0084 | Working Mail Delivery | DONE |
| TH-0085 | Multi-User Operational Readiness | DONE |
| TH-0086 | Recipe Ownership Foundation | DONE |
| TH-0087 | Recipe Publication and Moderation | DONE |
| TH-0088 | Dish Recipe Variants and Generation Modes | DONE |
| TH-0089 | Actor-Aware Audit Foundation | DONE |
| TH-0090 | Consolidated Russian Export Completeness | DONE |
| TH-0091 | Central Alcohol Prohibition | DONE |
| TH-0092 | Product Acceptance and Feature Freeze | DONE |
| TH-0093 | Final Migration and Release Readiness | DONE |

Details are stored in `./closed/` using the task ID and descriptive slug.

## Rules

- One logical change = one task.
- Completed tasks are moved to `closed/` after verification.
- Architectural decisions are documented separately.
- Current status documents override historical task wording when scope has been explicitly deferred.
- Post-release work cannot rewrite tag `v0.1.0` or silently expand its feature-frozen baseline.
- New product behavior requires an explicit Product Owner decision; documented debt-reduction work may proceed as an independently reviewable task.
