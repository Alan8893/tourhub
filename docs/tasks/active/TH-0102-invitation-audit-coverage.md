# TH-0102 — Invitation Lifecycle and Delivery-Result Audit Coverage

Status: IN PROGRESS

Started: 2026-07-20

## Goal

Add semantic actor-attributed AuditEvent coverage to the existing invitation lifecycle and automatic delivery-result boundary without changing invitation validity or exposing protected values.

## Scope

- audit successful invitation creation, reissue, revocation, and acceptance in their owning transactions;
- attribute create/reissue/revoke to the authenticated Administrator and acceptance to the newly created User snapshot;
- audit the automatic invitation delivery result after create/reissue at the existing post-commit result boundary;
- use bounded safe snapshots and context that exclude raw invitation tokens, acceptance links, passwords, password hashes, raw sessions, session hashes, SMTP secrets, protocol transcripts, exception details, and arbitrary request bodies;
- keep invitation creation/reissue valid when delivery is unavailable or fails;
- expose Russian Invitation labels and filtering in the existing Administrator Audit UI/API;
- add focused Backend and real-Chrome acceptance plus strict Ruff/mypy coverage.

## Out of scope

- asynchronous delivery, scheduled retry, delivery history tables, bounce processing, templates, or attachments;
- invitation retention/cleanup, account recovery, session administration, or user-profile changes;
- catalogue/import, shopping, equipment, or document-generation audit;
- ORM-wide auditing, migration, architecture/runtime changes, or release-tag movement.

## Definition of done

- invitation create, reissue, revoke, and accept append one semantic event in the owning transaction;
- failed persistence or audit recording rolls back the invitation/user/session mutation together;
- delivery-result events contain only safe status, attempt count, recipient domain, invitation ID, and operation kind;
- raw invitation/session/password/SMTP values never appear in AuditEvent;
- real-Chrome Audit acceptance shows Russian Invitation labels/filtering without mobile overflow;
- all repository workflows pass on one exact final head;
- current documentation and task state are synchronized before squash merge.
