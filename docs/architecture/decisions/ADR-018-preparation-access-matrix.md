# ADR-018 — Preparation Access Matrix

Status: Accepted

Date: 2026-07-18

## Context

TourHub now has operational accounts and roles. Administrative settings are already restricted, while the preparation workspace still needs one consistent access boundary. Module visibility is presentation only.

## Decision

Public capabilities remain limited to service health, initial setup, sign-in, and invitation acceptance.

The existing preparation workspace is available to active users with any approved first-release role:

- Administrator;
- Instructor;
- Verified Instructor.

This includes projects, catalogue, import, menu, shopping, equipment, documents, dishes, and current recipe operations.

Administrative settings, invitation management, and user management remain available only to Administrator.

Backend router groups apply one shared preparation dependency. The frontend wraps the complete `AppLayout` tree with one signed-in guard and preserves the requested path through the sign-in screen. Frontend behavior is supplementary; Backend checks remain authoritative.

Recipe publication, review, rejection, and club-library maintenance are not differentiated yet. Those permissions will be introduced with recipe ownership and lifecycle state.

Release runtime checks perform initial setup or sign-in before creating and reading the persistence-smoke project.

No database migration is required. The Alembic head remains `h10016`.

## Consequences

- anonymous preparation use is removed;
- all three approved roles retain current preparation workflows;
- onboarding and invitation acceptance remain reachable;
- the matrix is centralized and covered by API and browser tests;
- project ownership, detailed recipe permissions, audit actors, and account recovery remain separate work.
