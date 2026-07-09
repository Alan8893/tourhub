# TourHub — START HERE

## Purpose

This document is the entry point for any new developer, AI agent, or new chat session.

Before starting work, read this document and all linked documentation.

---

# Roles

## Product Owner

Responsible for:

- business decisions;
- feature priorities;
- final approval of architectural changes.

## Development Agent

Works as:

- CTO;
- Software Architect;
- Backend Engineer;
- Frontend Engineer;
- Code Reviewer.

---

# Source of Truth

Priority order:

1. Repository code.
2. Documentation in docs/.
3. ADR decisions.
4. Active tasks.

Never invent missing requirements.

---

# Mandatory Reading Order

Before any implementation:

1. docs/START_HERE.md
2. docs/PROJECT_CONTEXT.md
3. docs/ARCHITECTURE.md
4. docs/DOMAIN.md
5. docs/DEVELOPMENT_RULES.md
6. docs/architecture/DOMAIN_BOUNDARIES.md
7. Relevant ADR documents
8. Current task from docs/tasks/
9. Roadmap documents

---

# Architecture Principles

TourHub uses:

- Modular Monolith;
- Feature First;
- Vertical Slice Architecture;
- Clean Architecture principles.

The system is designed for long-term modular expansion.

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

Move task to closed

↓

Review roadmap

↓

Create next active task

---

# Current Product Direction

TourHub is an internal ERP system for one tourist club.

One system instance represents one club.

Future modules may include:

- Participants;
- Logistics;
- Routes;
- Equipment.

Modules are activated and developed independently.

---

# Important Rules

- Documentation first.
- Architecture changes require ADR.
- One logical task = one commit.
- Existing modules must not be broken by new modules.
- Frontend contains UI only.
- Business logic belongs to backend domains and engines.

---

# New Chat Template

Use:

"I am Product Owner.

You work as CTO, Software Architect, Backend Engineer, Frontend Engineer and Code Reviewer.

You have access to the repository.

Before starting, read docs/START_HERE.md and all required linked documentation."
