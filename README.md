# TourHub

TourHub is a local ERP application for preparing tourist-club trips: projects, meal plans, dishes, recipes, shopping projections, equipment, branded Russian exports, and operational backup/restore.

One installation represents one tourist club. The feature-frozen first release supports Administrator bootstrap, invitation-only multi-user access, explicit roles, guarded preparation workflows, working SMTP invitation delivery, multi-session readiness, CLUB/PERSONAL Recipe ownership, publication/moderation with rejection feedback, ordered Recipe variants per Dish, project-level generation modes with persisted assignment Recipe snapshots, an append-only actor-aware audit foundation, complete consolidated Russian Project PDF/XLSX exports, and one centralized no-exceptions alcohol policy across Product, Recipe, Dish, API, and CSV import paths. The only remaining release-blocking phase is Final Migration and Release Readiness.

## Quick start

Use the production-like release stack for an operator installation:

```bash
docker compose -f docker-compose.release.yml up -d --build --wait
curl -fsS http://localhost:8000/api/v1/health
curl -fsS http://localhost:5173/healthz
```

After startup on the server:

- frontend: `http://localhost:5173`;
- backend API: `http://localhost:8000`;
- OpenAPI: `http://localhost:8000/docs`.

From another computer on the same trusted network, open:

```text
http://<server-ip>:5173
```

Frontend API calls use the same origin under `/api/v1` and are proxied by the frontend Nginx container to the Backend. Browser-facing code must not hardcode `localhost:8000`, because `localhost` would refer to the user's computer rather than the TourHub server.

Database migrations run through the Backend container entrypoint. PostgreSQL data is stored in the `postgres18_cluster_data` named Docker volume. The release stack does not publish PostgreSQL or Redis ports.

The default `docker-compose.yml` remains the development-oriented stack with source bind mounts and infrastructure ports.

## Operator documentation

- [Installation runbook](docs/INSTALLATION.md) — prerequisites, first startup, health checks, LAN access, backups, and routine operations;
- [Docker release runtime](docs/DOCKER_RELEASE.md) — immutable images, release Compose, health contract, internal services, and automated runtime validation;
- [Update and recovery runbook](docs/UPDATING.md) — backup-first update, explicit migrations, verification, restore, and rollback boundaries.

Create a release-stack host-side PostgreSQL custom-format backup:

```bash
COMPOSE_FILE=docker-compose.release.yml bash scripts/db/backup-tourhub.sh
```

Restore requires an explicit confirmation flag and leaves application services stopped:

```bash
COMPOSE_FILE=docker-compose.release.yml \
  bash scripts/db/restore-tourhub.sh backups/<dump-file>.dump --confirm
```

## Canonical documentation

Use these documents for current decisions:

- [`docs/PRODUCT_SPEC.md`](docs/PRODUCT_SPEC.md) — approved full product target;
- [`docs/PRODUCT_ACCEPTANCE.md`](docs/PRODUCT_ACCEPTANCE.md) — accepted feature-frozen first-release scope and deferred non-blocking capabilities;
- [`docs/product_acceptance_manifest.json`](docs/product_acceptance_manifest.json) — machine-readable acceptance source of truth;
- [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) — verified implemented state;
- [`docs/CURRENT_ROADMAP.md`](docs/CURRENT_ROADMAP.md) — delivery order and selected release scope;
- [`docs/ARCHITECTURE_CURRENT.md`](docs/ARCHITECTURE_CURRENT.md) — current architecture boundaries;
- [`docs/DOMAIN_CURRENT.md`](docs/DOMAIN_CURRENT.md) — current persisted domain;
- [`docs/TECH_DEBT.md`](docs/TECH_DEBT.md) — active and completed debt;
- [`docs/tasks/TASKS.md`](docs/tasks/TASKS.md) — active and closed task index.

`PRODUCT_SPEC.md` describes the approved full target, including capabilities intentionally deferred from the current release. `PRODUCT_ACCEPTANCE.md`, `CURRENT_ROADMAP.md`, and `PROJECT_STATUS.md` define the accepted implementation and the only remaining release-readiness work. Current documents and accepted ADRs override historical files under archive or legacy directories.

## Quality gates

GitHub Actions enforce:

- Backend tests;
- selected Ruff and strict mypy baselines;
- Alembic single-head validation;
- Frontend tests, production build, and browser acceptance;
- dedicated Product Acceptance manifest, selected Backend API/migration, and six critical Chrome scenarios;
- guided desktop/mobile create-to-ZIP release acceptance;
- moderate-severity dependency audit;
- PostgreSQL 18 backup/restore smoke testing;
- operator runbook and script validation;
- production-like Docker image build and clean runtime smoke testing.

## Development rules

- one logical change per task and pull request;
- migrations must keep exactly one Alembic head;
- Backend owns calculations, import validation, transaction boundaries, identity, authorization, lifecycle, generation, audit, document content, and central catalogue policies;
- Frontend owns presentation, navigation, form state, and API integration;
- Frontend features use the shared API client and do not hardcode browser-visible service origins;
- first-release scope is feature frozen: only acceptance defects, security fixes, final release-readiness work, and documentation corrections are allowed without a new Product Owner decision;
- documentation must be synchronized when product, domain, architecture, persistence, or release scope changes.
