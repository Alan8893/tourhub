# TourHub AI Agent Contract

Version: 1.0

This document defines mandatory rules for any AI agent working on the TourHub project.

These rules apply to Claude Code, ChatGPT, Cursor, GitHub Copilot Agent and any future AI assistant.

Ignoring these rules is considered an implementation error.

---

# 1. Project Goal

TourHub is an ERP system for tourist clubs.

The MVP goal is automatic generation of hiking packing lists:

Menu
→ Products
→ Packing
→ Packaging
→ Purchase list
→ PDF / Excel

The project is intended for long-term development.

Architecture stability has higher priority than implementation speed.

---

# 2. Required Reading Order

Before performing ANY task the AI MUST read:

1.
docs/PROJECT_CONTEXT.md

2.
docs/ARCHITECTURE.md

3.
docs/DOMAIN.md

4.
docs/DEVELOPMENT_RULES.md

5.
docs/TASKS.md

If one of these files is missing or contradictory —

STOP.

Report the problem.

Do NOT continue.

---

# 3. Source of Truth

The source of truth is:

Repository

↓

Documentation

↓

Current task

Never use assumptions.

Never invent missing architecture.

Never ignore documentation.

---

# 4. Product Owner

The Product Owner always has the final decision.

The AI never argues with business requirements.

The AI may suggest improvements.

The AI must never silently change requirements.

---

# 5. Architecture

The architecture is frozen.

Changing architecture is prohibited.

Changing directory structure is prohibited.

Changing module boundaries is prohibited.

Changing dependency direction is prohibited.

Changing project layout is prohibited.

Unless the Product Owner explicitly approves the change.

---

# 6. Architecture Changes

If the AI believes architecture should change:

STOP.

Provide:

1.
Problem

2.
Impact

3.
Advantages

4.
Disadvantages

5.
Suggested solution

Wait for approval.

---

# 7. Development Process

For every task:

Design

↓

Implementation

↓

Self Review

↓

Validation

↓

Stop

Never continue to another task automatically.

---

# 8. Tasks

Always execute ONLY the first unfinished task from:

docs/TASKS.md

Never skip tasks.

Never reorder tasks.

Never create new tasks.

---

# 9. Definition of Done

A task is complete only if:

✓ code is implemented

✓ project builds

✓ tests pass

✓ documentation updated

✓ no TODO

✓ no FIXME

✓ no placeholder

---

# 10. Code Quality

Write production-ready code.

Never write demo code.

Never write temporary code.

Never leave unfinished implementations.

No dead code.

No commented code.

No duplicated code.

---

# 11. Backend Rules

Backend contains business logic.

Business logic must never exist inside Frontend.

Business logic must never exist inside API routes.

Business logic belongs to modules and engines.

---

# 12. Engines

Engines are pure calculations.

Input:

DTO

Output:

DTO

Engine must never:

- access database

- call HTTP

- know FastAPI

- know SQLAlchemy

- know repositories

---

# 13. Frontend

Frontend contains only UI.

No business logic.

No calculations.

No domain rules.

---

# 14. Dependencies

Never add new dependency unless required.

If a new dependency is required:

Explain:

Why

Alternatives

Impact

Wait for approval.

---

# 15. Git

One logical task

=

One commit.

Use Conventional Commits.

Examples:

feat:

fix:

refactor:

docs:

test:

chore:

---

# 16. Testing

Every feature must be testable.

If tests cannot be written,

explain why.

---

# 17. Documentation

Whenever architecture changes,

documentation must be updated first.

Code follows documentation.

Never the opposite.

---

# 18. Communication

When the task is complete always provide:

## Completed

Short summary.

## Files Changed

List of modified files.

## Validation

How to verify.

## Risks

Potential risks.

## Next Step

Wait for Product Owner.

---

# 19. Forbidden

Never:

- change architecture

- change project structure

- rename modules

- invent requirements

- skip tasks

- continue automatically

- remove existing functionality without approval

- ignore documentation

---

# 20. Success Criteria

The AI succeeds if:

Architecture remains consistent.

Documentation remains correct.

Code is production-ready.

Every commit can be reviewed independently.

Every task can be reverted independently.

The project remains understandable for new developers.