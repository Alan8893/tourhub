# ADR-010 — Modular Feature Architecture

Status:

Accepted

Date:

2026-07-09

---

# Context

TourHub is planned as a long-term ERP product.

The system must grow without breaking existing business domains.

---

# Decision

TourHub uses modular feature architecture.

Each business capability is an independent module with clear boundaries.

---

# Principles

1. New modules must not break existing modules.

2. Business logic belongs to its own domain module.

3. Modules communicate through contracts and interfaces.

4. Architecture changes require approval and ADR.

5. Features can be enabled by system configuration in the future.

---

# Example Future Expansion

Adding Participants module:

```
Project
 |
 + Participants
 + Nutrition
 + Shopping
 + Documents
```

Existing Nutrition logic should continue working.

---

# Scope

This ADR defines architecture direction.

It does not implement module activation, feature flags, or new domains.
