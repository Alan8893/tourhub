# TH-0072 — Docker Release Runtime Validation

Status: DONE

Completed: 2026-07-17

## Goal

Provide an immutable, production-like Docker startup path and verify that a clean TourHub stack can build, migrate, start, serve the UI and API, and preserve application data across container restarts.

## Delivered

- standalone `docker-compose.release.yml` without application source bind mounts;
- multi-stage frontend image with a built Vite application served by Nginx;
- same-origin `/api/` proxy and explicit frontend/backend health checks;
- PostgreSQL and Redis restricted to the internal Compose network;
- clean image build and clean-environment startup in GitHub Actions;
- API project creation and persistence verification after application restart;
- current Alembic head verification;
- focused diagnostics and unconditional stack cleanup;
- synchronized installation, update, backup, and restore guidance.

## Validation

Exact PR #80 head `73b233f7529d5d310a750071d592e9b108b9a1df` passed:

- Quality #454;
- Document Quality #84;
- Guided Release Acceptance #35;
- Operator Docs #21;
- Docker Release Runtime #17.

PR #80 merged into `main` as `939828e8c335966dde2d04c5083ee7d2da07c6eb`.

## Preserved boundaries

- explicit PostgreSQL downgrade/re-upgrade smoke remains after feature freeze;
- public-internet deployment, TLS termination, and multi-tenant hardening remain out of scope;
- the named PostgreSQL volume remains the persistence boundary.
