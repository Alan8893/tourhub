# TourHub — START HERE

## Purpose

This document is the entry point for every developer, AI agent, and new chat session.

Before starting work, read this document and the required linked documentation.

---

# Roles

## Product Owner

Responsible for:

- business decisions;
- feature priorities;
- changes to MVP scope;
- approval of technology stack changes;
- final product acceptance.

## Development Agent

Works as:

- CTO;
- Software Architect;
- Backend Engineer;
- Frontend Engineer;
- Code Reviewer;
- Documentation Maintainer.

The Development Agent may independently implement, review, document, and merge technical changes that remain inside the approved product model and technology stack.

---

# Source of Truth

Priority order:

1. Accepted product decisions in `docs/PRODUCT_SPEC.md`.
2. Repository code and executable tests.
3. `docs/ARCHITECTURE_CURRENT.md` and `docs/DOMAIN_CURRENT.md`.
4. `docs/PROJECT_STATUS.md`.
5. Extended architecture and domain documentation.
6. Accepted ADR decisions.
7. Current active task.
8. Roadmap documents.

Never invent missing business requirements.

When code and documentation disagree, stop feature work, determine the implemented behavior, and synchronize the documentation before closing the task.

---

# Mandatory Reading Order

Before any implementation:

1. `docs/START_HERE.md`
2. `docs/PRODUCT_SPEC.md`
3. `docs/PROJECT_STATUS.md`
4. `docs/PROJECT_CONTEXT.md`
5. `docs/ARCHITECTURE_CURRENT.md`
6. `docs/DOMAIN_CURRENT.md`
7. `docs/ARCHITECTURE.md` and `docs/DOMAIN.md` as extended references
8. `docs/DEVELOPMENT_RULES.md`
9. `docs/architecture/DOMAIN_BOUNDARIES.md`
10. Relevant ADR documents, including ADR-012
11. Current task from `docs/tasks/active/`
12. `docs/CURRENT_ROADMAP.md`
13. `docs/TECH_DEBT.md` when the task affects stabilization or quality

---

# Product Boundaries

TourHub is a local ERP system for one tourist club.

- One installation represents one club.
- Multi-tenant support is prohibited.
- The application is designed for a closed local environment.
- Registration is invitation-only.
- MVP roles are Administrator, Instructor, and Verified Instructor.
- Alcohol is prohibited without exceptions.
- Participant personal profiles are a future module; MVP calculations use participant count only.

---

# Architecture Principles

TourHub uses:

- Modular Monolith;
- Feature First;
- Vertical Slice Architecture;
- Clean Architecture principles;
- evolutionary migrations for existing data models.

Frontend contains UI and client state only. Business rules belong to backend domains, services, and engines.

Technology stack changes require Product Owner approval. Microservices and multi-tenant infrastructure are prohibited.

---

# Task Lifecycle

Every task follows:

Design

↓

Implementation

↓

Backend verification

↓

Frontend verification

↓

Documentation update

↓

Technical review

↓

Pull Request

↓

Merge

↓

Move task to closed

↓

Update project status, roadmap, and technical debt

↓

Create or activate the next task

A task is not closed merely because code has been written or committed.

---

# Definition of Done

A task may be closed only when:

- all acceptance criteria are satisfied;
- relevant backend tests pass;
- relevant frontend checks pass;
- migrations are valid when persistence changed;
- no temporary code or TODO remains in task scope;
- public API contracts are verified;
- documentation matches the implementation;
- task status and roadmap are updated;
- known remaining work is recorded as a separate task or technical debt item.

---

# Important Rules

- Documentation first and documentation with code.
- Architecture changes require ADR.
- One logical task should produce one squash commit in `main`.
- Existing modules must not be broken by new modules.
- Technical fixes may be merged autonomously after successful verification.
- Product model, MVP boundaries, and stack changes require Product Owner approval.
- No paid services for MVP.
- All runtime services remain local.

---

# New Chat Template

Use:

"I am Product Owner.

You work as CTO, Software Architect, Backend Engineer, Frontend Engineer, Code Reviewer, and Documentation Maintainer.

You have access to the repository.

Before starting, read `docs/START_HERE.md` and all mandatory linked documentation. Continue from the current active task and do not reopen closed tasks without evidence of a regression."
