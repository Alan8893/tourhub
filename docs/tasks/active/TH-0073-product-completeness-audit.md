# TH-0073 — Product Completeness Audit

Status: IN PROGRESS

Last updated: 2026-07-17

## Goal

Reconcile the approved product specification with the implemented TourHub application, place final migration/release hardening after feature freeze, and record the Product Owner-selected implementation order.

## Scope

- verify implementation status for every `PRODUCT_SPEC.md` area;
- distinguish implemented, partial, missing, future, and Product Owner decision items;
- preserve the merged production-like Docker runtime as the platform for later work;
- keep basic Alembic, PostgreSQL, backup/restore, Docker, and full Quality gates mandatory;
- defer final downgrade/re-upgrade smoke until feature freeze;
- record System Settings foundation as the next capability before access foundation;
- synchronize roadmap, status, technical debt, and task sequencing.

## Acceptance criteria

- `docs/PRODUCT_COMPLETENESS_AUDIT.md` records evidence and a completeness matrix;
- unified system settings, access/roles, recipe lifecycle, alcohol prohibition, audit logging, and consolidated exports have explicit statuses;
- existing project-preparation functionality is not incorrectly reopened;
- PR #80 is recorded as merged and TH-0072 is closed;
- final migration smoke remains deferred while existing safety gates remain mandatory;
- full Quality and all applicable focused workflows pass on the exact PR head;
- the PR remains documentation-only.

## Product Owner sequencing decision

The next implementation slice is **System Settings foundation**, not multi-user access.

Detailed requirements must be clarified before implementation, including:

- page sections and navigation;
- branding and appearance customization;
- typed module settings;
- invitation configuration versus actual invitation workflow;
- mail provider and secret-handling requirements;
- permissions, defaults, reset behavior, validation, and audit expectations.

## Out of scope

- System Settings implementation code;
- authentication, users, or authorization implementation;
- recipe ownership or moderation implementation;
- alcohol-policy implementation;
- audit-log implementation;
- document-generator implementation;
- final migration cycle or release tagging.

## Follow-up sequence

1. System Settings foundation.
2. Access foundation and functional invitations.
3. Recipe ownership and lifecycle.
4. Central alcohol prohibition.
5. Actor-aware audit log.
6. Consolidated export completeness.
7. Product acceptance and feature freeze.
8. Final migration and release gates.

## Definition of done

- the first-release sequence follows explicit Product Owner decisions;
- every deferred capability is visible and deliberate;
- one logical capability remains one pull request;
- exact-head CI is green;
- no runtime behavior changes are introduced by the audit.
