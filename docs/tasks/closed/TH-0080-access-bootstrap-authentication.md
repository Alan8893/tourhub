# TH-0080 — Access Bootstrap and Authentication

Status: DONE

Last updated: 2026-07-18

## Goal

Introduce the first operational identity boundary for one local TourHub installation: create the first Administrator exactly once, authenticate with server-owned sessions, and protect System Settings without mixing in the functional invitation lifecycle.

## Delivered

- typed User, IdentityState, and AuthSession persistence;
- one-time transactionally locked Administrator bootstrap;
- scrypt password hashing with random salts;
- login, logout, current-user and bootstrap-status endpoints;
- opaque HttpOnly SameSite sessions with only token hashes stored in PostgreSQL;
- Administrator authorization for all System Settings APIs and `/settings`;
- responsive bootstrap/login UX, current-user display and logout;
- additive Alembic head `h10014`;
- exact-head Quality, document, operator, guided acceptance, PostgreSQL and Docker validation.

## Scope boundary retained

Functional invitations, user administration, broad preparation authorization, password reset and mail delivery remain separate follow-up capabilities.

## Completion

Merged through PR #90 as commit `26c4d4eb9246de44579451fe3d6e7bd631538324`.
