# TH-0073 — Product Completeness Audit

Status: IN PROGRESS

Last updated: 2026-07-17

## Goal

Reconcile the approved product specification with the implemented TourHub application and move final migration/release hardening after the remaining release-blocking user and domain capabilities.

## Scope

- verify implementation status for every `PRODUCT_SPEC.md` section;
- distinguish implemented, partial, missing, explicitly future, and Product Owner decision items;
- identify release-blocking access, recipe lifecycle, domain-safety, audit, and export gaps;
- preserve the validated Docker runtime slice in PR #80 as an independent prerequisite;
- update the roadmap so final migration downgrade/re-upgrade smoke runs after feature freeze;
- define an implementation order without adding feature code in the audit PR.

## Acceptance criteria

- `docs/PRODUCT_COMPLETENESS_AUDIT.md` records the evidence and completeness matrix;
- access/roles, recipe ownership/moderation, alcohol prohibition, audit logging, and consolidated exports have explicit statuses;
- existing implemented project preparation is not incorrectly reopened;
- migration smoke remains deferred, while existing Alembic, PostgreSQL, backup/restore, and Docker gates remain mandatory;
- roadmap, status, technical debt, and task index are synchronized;
- full Quality and all applicable focused workflows pass on the exact PR head;
- the PR remains documentation-only and does not alter runtime behavior.

## Out of scope

- merging PR #80;
- authentication or authorization implementation;
- recipe ownership, variants, publication, or moderation implementation;
- alcohol-policy implementation;
- audit-log implementation;
- document generator implementation;
- migration downgrade/re-upgrade smoke;
- final release tagging.

## Follow-up sequence

1. Access foundation.
2. Recipe ownership and lifecycle.
3. Central alcohol prohibition.
4. Actor-aware audit log.
5. Consolidated export completeness.
6. Product acceptance and feature freeze.
7. Final migration and release gates.

## Definition of done

- the first-release sequence is based on the approved product specification rather than only the current narrow single-user flow;
- every deferred capability requires an explicit Product Owner decision;
- one logical capability remains one pull request;
- PR #80 remains independently mergeable and reviewable.
