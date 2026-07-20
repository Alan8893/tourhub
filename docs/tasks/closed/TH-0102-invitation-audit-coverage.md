# TH-0102 — Invitation Lifecycle and Delivery-Result Audit Coverage

Status: DONE

Started: 2026-07-20

Completed: 2026-07-20

## Delivered

- invitation creation, reissue, revocation, and acceptance append semantic actor-attributed AuditEvents in their owning SQLAlchemy transactions;
- create, reissue, and revoke use the authenticated Administrator snapshot, while acceptance uses the newly created User snapshot;
- lifecycle audit failure rolls back pending invitation, User, AuthSession, and AuditEvent changes together;
- create/reissue automatic delivery records a separate safe result event after the invitation commit;
- delivery results contain only status, attempt count, recipient domain, operation kind, role, and Invitation ID;
- delivery or delivery-audit failure preserves the valid invitation and one-time manual link;
- raw invitation tokens, acceptance links, passwords and hashes, sessions and hashes, SMTP secrets, provider messages, protocol transcripts, exception details, full recipient addresses, and arbitrary request bodies are excluded;
- the Administrator Audit surface exposes Russian Invitation labels and filtering with responsive real-Chrome coverage.

## Verification

Candidate implementation head `dab3e071a13d131b5dc2a7d890923faeffe2c55c` passed strict Ruff/mypy, the full Backend test suite, Frontend tests/build/browser acceptance, Product Acceptance, PostgreSQL backup/restore, Alembic single-head validation, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness.

The final documentation-only head is verified again before merge.

## Excluded

- asynchronous mail, scheduled retries, persisted delivery history, bounce processing, templates, attachments, invitation retention/cleanup, recovery, session administration, and user-profile changes;
- catalogue/import, shopping, equipment, and document-generation audit;
- ORM-wide auditing, migrations, architecture/runtime changes, product-scope expansion, and release-tag movement.
