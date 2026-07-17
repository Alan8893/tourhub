# TH-0072 — Docker Release Runtime Validation

Status: IN PROGRESS

Last updated: 2026-07-17

## Goal

Provide an immutable, production-like Docker startup path and verify that a clean TourHub stack can build, migrate, start, serve the UI and API, and preserve application data across container restarts.

## Scope

- standalone release Compose file without source bind mounts;
- multi-stage frontend image with a built Vite application served by Nginx;
- same-origin `/api/` proxy and explicit frontend/backend health checks;
- PostgreSQL and Redis available only on the internal Compose network;
- clean image build and clean-environment startup in GitHub Actions;
- API project creation and persistence verification after backend/frontend restart;
- current Alembic head verification after startup;
- focused Docker diagnostics and unconditional stack cleanup.

## Acceptance criteria

- `docker compose -f docker-compose.release.yml config` renders successfully;
- backend and frontend run from built images without application bind mounts;
- PostgreSQL and Redis do not publish host ports;
- release images build with fresh base-image pulls;
- the clean stack reaches healthy state within the workflow timeout;
- frontend `/healthz`, backend `/api/v1/health`, and proxied `/api/v1/health` succeed;
- the built frontend application shell is served by Nginx;
- a project created through the frontend proxy remains readable after application container restart;
- the database reports the current Alembic head;
- full Quality, Document Quality, Guided Release Acceptance, Operator Docs, and Docker Release Runtime workflows pass on the exact PR head.

## Out of scope

- explicit PostgreSQL migration upgrade/downgrade smoke across revisions;
- release tagging, changelog generation, and final release workflow;
- public-internet deployment, TLS termination, secrets management platform integration, or multi-tenant hardening.
