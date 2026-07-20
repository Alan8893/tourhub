# TH-0101 — System Settings and Mail Audit Coverage

Status: DONE

Started: 2026-07-19

Completed: 2026-07-20

## Goal

Add semantic actor-attributed audit events to System Settings changes and Administrator mail operations while preserving existing behavior and excluding secrets.

## Delivered

- Club, Appearance, Document Appearance, Module, Invitation Policy, and Mail Settings changes record semantic events with the authenticated Administrator;
- settings snapshots contain only changed normalized fields and version transitions;
- no-op settings saves create no AuditEvent;
- existing settings mutation, focused settings history, and AuditEvent share one owning commit/rollback transaction;
- legacy and typed Club write paths use the same `club_settings_updated` boundary;
- Club image changes record configured state, MIME type, and byte size without binary data or data URLs;
- SMTP connection checks and fixed test-message operations record safe `sent`, `failed`, or `unavailable` result metadata at the existing result boundary;
- SMTP passwords, environment values, protocol transcripts, exception details, invitation/session values, tokens, and arbitrary request bodies are not stored;
- the Administrator Audit UI/API exposes Russian System Settings and Mail labels and filtering;
- focused Backend coverage verifies every settings owner, actor attribution, no-op suppression, redaction, success/failure outcomes, and rollback;
- real-Chrome acceptance verifies Russian labels, filtering, and mobile containment.

## Verification

Candidate implementation head `b645bd3e90302c99dc3e64c29bde23ad58b79a29` passed strict Ruff/mypy, the full Backend test suite, Frontend tests/build/browser acceptance, Product Acceptance, PostgreSQL backup/restore, Alembic single-head validation, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness.

The documentation closure head is verified again before squash merge.

## Excluded

- invitation lifecycle auditing, asynchronous delivery, retries, bounce processing, templates, or attachments;
- audit of Project/Menu/Recipe/User paths already covered by earlier tasks;
- ORM-wide auditing, secret storage changes, migration, architecture/runtime changes, or release-tag movement.
