# TourHub Development Rules

Version: 2.0

Status: Active

Last Updated: 2026-07-14

## 1. Mandatory Reading

Before implementation, read in order:

1. `START_HERE.md`;
2. `PRODUCT_SPEC.md`;
3. `PROJECT_STATUS.md`;
4. `PROJECT_CONTEXT.md`;
5. `ARCHITECTURE_CURRENT.md`;
6. `DOMAIN_CURRENT.md`;
7. `ARCHITECTURE.md` and `DOMAIN.md` as extended legacy references;
8. `DEVELOPMENT_RULES.md`;
9. domain boundaries and relevant ADRs;
10. the current active task;
11. `CURRENT_ROADMAP.md` and `TECH_DEBT.md`.

Missing business requirements must not be invented.

## 2. Source of Truth

Priority:

1. approved Product Owner decisions in `PRODUCT_SPEC.md`;
2. verified repository code and tests;
3. `ARCHITECTURE_CURRENT.md` and `DOMAIN_CURRENT.md`;
4. current status and roadmap;
5. extended architecture and domain documentation;
6. accepted ADRs;
7. active task documents.

Contradictions must be resolved in the same task.

## 3. Task Lifecycle

A task follows:

```text
DRAFT -> READY -> ACTIVE -> READY FOR REVIEW -> READY FOR ACCEPTANCE -> CLOSED
```

`BLOCKED` and `CANCELLED` may be used when justified.

A task is CLOSED only when:

- agreed behavior is implemented;
- backend verification passes;
- frontend verification passes when applicable;
- migrations are valid;
- documentation is synchronized;
- roadmap and project status are updated;
- no known in-scope regression remains.

## 4. Git and Pull Requests

- Work in a dedicated branch.
- Use Conventional Commits.
- One logical task is delivered as one squash commit in `main`.
- Technical PRs may be merged autonomously after successful verification.
- Product-model, stack, or MVP-boundary changes require Product Owner approval.

## 5. Production-Ready Rule

Forbidden:

- TODO placeholders in delivered scope;
- public `NotImplementedError` endpoints;
- temporary domain models;
- silent fallback that hides invalid state;
- business logic in Frontend;
- direct database access from Frontend or Engines;
- microservices or multi-tenant infrastructure;
- paid external services without approval.

## 6. Quality Gates

Required as applicable:

- backend tests;
- frontend tests;
- Ruff;
- mypy;
- TypeScript check and production build;
- Alembic single-head validation;
- Docker Compose startup;
- dependency/security audit.

Existing Ruff and mypy debt may be reduced incrementally, but every PR must not increase the baseline.

## 7. Documentation Updates

Update together with code:

- business rules -> `PRODUCT_SPEC.md`, `DOMAIN_CURRENT.md`, and relevant legacy domain sections;
- architecture -> ADR, `ARCHITECTURE_CURRENT.md`, and relevant legacy architecture sections;
- implementation state -> `PROJECT_STATUS.md`;
- delivery order -> `CURRENT_ROADMAP.md`;
- known debt -> `TECH_DEBT.md`;
- task result -> move task from `active` to `closed`.

## 8. Security and Privacy

- Registration is invitation-only.
- Secrets, passwords, and tokens are never logged or committed.
- Audit logs contain actor, action, timestamp, and safe metadata only.
- Alcohol prohibition is enforced in Backend domain validation.
- The system is local-first and does not transmit club data to external paid services.
