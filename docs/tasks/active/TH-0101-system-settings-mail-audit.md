# TH-0101 — System Settings and Mail Audit Coverage

Status: IN PROGRESS

Started: 2026-07-19

## Goal

Add semantic actor-attributed audit events to System Settings changes and Administrator mail operations while preserving existing behavior and excluding secrets.

## Scope

- audit successful club, appearance, document-appearance, module-visibility, invitation-policy, and mail-setting changes in their owning transactions;
- audit Administrator mail test/delivery operations at the existing result boundary;
- use bounded before/after/context snapshots that exclude SMTP passwords, session tokens, invitation tokens, and other protected values;
- suppress no-op settings events;
- failures roll back settings changes and pending AuditEvents together where persistence is transactional;
- expose Russian System Settings and Mail labels in the existing Administrator Audit UI/API;
- add focused Backend and real-Chrome acceptance and strict Ruff/mypy coverage.

## Out of scope

- invitation lifecycle auditing, asynchronous delivery, retries, bounce processing, templates, or attachments;
- audit of Project/Menu/Recipe/User paths already covered by earlier tasks;
- ORM-wide auditing, secret storage changes, migration, architecture/runtime changes, or release-tag movement.

## Definition of done

- every approved settings owner records one semantic event only when persisted values change;
- mail operations record safe outcome metadata without protected configuration values;
- actor attribution, no-op suppression, redaction, success, and rollback behavior are tested;
- real-Chrome Audit acceptance shows Russian labels/filtering without mobile overflow;
- all repository workflows pass on one exact final head;
- current documentation and task state are synchronized before squash merge.
