# ADR-012 — Single-Club Closed-Access MVP Boundaries

Status: Accepted

Date: 2026-07-14

## Context

Legacy documentation contained conflicting statements about one-club deployment and multi-tenant organizations. Product Owner decisions define TourHub as a local ERP for one tourist club with sensitive information and invitation-only access.

## Decision

### Deployment

- One TourHub installation represents exactly one tourist club.
- Multi-tenant architecture is prohibited.
- MVP runs locally through Docker Compose.
- Paid external services are not used.

### Access

- Registration is available only through administrator invitations.
- MVP roles are Administrator, Instructor, and Verified Instructor.
- Backend enforces permissions.
- Security-sensitive and business-significant changes are written to an audit log.

### Domain boundaries

- Participant profiles are not part of MVP; projects store participant count only.
- Dish and Recipe remain separate; recipe scopes are CLUB, PERSONAL, and ARCHIVED.
- Verified Instructor may publish and moderate club recipes.
- Alcohol is prohibited by backend domain rules.
- Shopping, packaging, equipment, and documents are part of MVP.
- Routes, logistics, warehouse balances, participant profiles, prices, and aggregators are future domains.

### Recalculation

Changing participant count or meal composition preserves selected dishes and recalculates dependent quantities, packages, shopping, and equipment.

## Consequences

- Tenant identifiers and organization-isolation infrastructure must not be added.
- Existing legacy organization wording is superseded.
- Invitation, roles, audit logging, and local backup/restore become mandatory MVP work.
- Future participant and logistics modules must be documented before implementation.

## Supersedes

This ADR supersedes every legacy statement that one installation may serve multiple organizations.
