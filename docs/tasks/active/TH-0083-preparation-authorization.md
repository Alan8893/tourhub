# TH-0083 — Preparation Authorization Matrix

Status: IN PROGRESS

Last updated: 2026-07-18

## Goal

Require an active TourHub session for all project-preparation interfaces and APIs while preserving the approved role boundaries for one local club.

## Role matrix

- Public: health, bootstrap/login/logout contract, and invitation inspection/acceptance.
- Administrator: all preparation capabilities plus System Settings, invitation management, and user administration.
- Instructor: project, catalogue, import, menu, shopping, equipment, document, dish, and current recipe capabilities.
- Verified Instructor: the same preparation capabilities as Instructor; publication and moderation distinctions remain part of the later recipe-lifecycle slice.

## Scope

### Backend

- add one explicit preparation-access dependency backed by the active server session;
- apply it to project, catalogue, import, menu, shopping, equipment, document, dish, and current recipe routers;
- keep health, authentication bootstrap/login, and public invitation acceptance available without a session;
- preserve Administrator-only dependencies for settings, invitation administration, and user administration;
- return HTTP 401 for missing, expired, revoked, or inactive-user sessions.

### Frontend

- guard the entire `AppLayout` preparation tree;
- redirect unauthenticated visitors to `/login` while preserving the requested destination;
- keep `/login` and `/accept-invitation` public;
- keep `/settings` additionally protected by the Administrator guard;
- avoid role-specific hiding for recipe publication/moderation until that domain is implemented.

## Out of scope

- recipe ownership, publication, review, rejection, and archive permissions;
- per-project ownership or row-level access;
- request-forgery hardening beyond the existing trusted-LAN session model;
- actor-aware audit history;
- password reset, MFA, external identity, or multi-tenancy.

## Acceptance criteria

- unauthenticated preparation API requests receive HTTP 401;
- active Administrator, Instructor, and Verified Instructor sessions can use preparation APIs;
- public health/auth/invitation-acceptance routes remain reachable;
- non-Administrator users still receive HTTP 403 for System Settings and administrative APIs;
- all preparation frontend routes redirect to login when signed out and return to the requested route after login;
- exact-head Quality, document, operator, guided acceptance, PostgreSQL, and Docker gates pass.