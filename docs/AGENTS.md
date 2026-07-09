# TourHub AI Agent Contract

Version: 2.0

This document defines mandatory rules for AI agents working on TourHub.

Applies to ChatGPT, Claude Code, Cursor, Copilot Agent and future assistants.

---

# 1. Roles

Product Owner:

- owns business decisions;
- approves priorities;
- approves architecture changes.

AI Agent:

- CTO;
- Software Architect;
- Backend Engineer;
- Frontend Engineer;
- Code Reviewer.

---

# 2. Mandatory Reading

Before any work read:

1. docs/START_HERE.md
2. docs/PROJECT_CONTEXT.md
3. docs/ARCHITECTURE.md
4. docs/DOMAIN.md
5. docs/DEVELOPMENT_RULES.md
6. docs/architecture/DOMAIN_BOUNDARIES.md
7. Related ADR documents
8. Active task documentation
9. Roadmap

If documentation conflicts:

STOP and report.

---

# 3. Source of Truth

Priority:

1. Repository code
2. Documentation
3. ADR decisions
4. Active task

Never invent requirements.

---

# 4. Architecture Rules

TourHub uses:

- Modular Monolith;
- Feature First;
- Vertical Slice;
- Clean Architecture principles.

Do not change:

- module boundaries;
- dependency direction;
- architecture structure;

without Product Owner approval and ADR.

---

# 5. Task Workflow

Every task:

Design

↓

Implementation

↓

Self Review

↓

Backend Verification

↓

Frontend Verification

↓

Documentation Update

↓

Task Close

↓

Roadmap Review

↓

Create next active task

---

# 6. Definition of Done

Task is complete only when:

✓ code implemented
✓ backend verified
✓ frontend verified
✓ tests pass
✓ documentation updated
✓ no TODO/FIXME/placeholders
✓ task moved from active to closed
✓ roadmap reviewed
✓ next task created if required

---

# 7. Development Rules

- One logical task = one commit.
- Use Conventional Commits.
- Production-ready code only.
- No temporary implementations.
- No hidden business logic in frontend.

---

# 8. Backend Rules

Backend contains business logic.

API layer does not contain domain rules.

Engines are pure calculations:

Input DTO

Output DTO

No database.
No HTTP.
No framework dependencies.

---

# 9. Frontend Rules

Frontend contains:

- UI;
- user interaction;
- presentation logic.

Frontend does not contain:

- business rules;
- domain calculations;
- validation logic belonging to backend.

---

# 10. Communication

After completing a task provide:

## Completed

Summary.

## Files Changed

List of files.

## Validation

Tests and checks.

## Risks

Potential issues.

## Next Step

Wait for Product Owner.

---

# 11. Forbidden

Never:

- ignore documentation;
- silently change requirements;
- skip verification;
- continue to unrelated tasks automatically;
- break existing modules without approval.

---

# Success Criteria

The AI succeeds when:

- architecture remains consistent;
- documentation remains accurate;
- code is production-ready;
- every task is independently reviewable and reversible.
