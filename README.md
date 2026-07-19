# TourHub

TourHub is a local ERP application for preparing tourist-club trips: projects, meal plans, dishes, recipes, shopping projections, equipment, branded Russian exports, and operational backup/restore.

One installation represents one tourist club. TourHub v0.1.0 is the feature-frozen first release: Administrator bootstrap, invitation-only multi-user access, explicit roles, guarded preparation workflows, working SMTP invitation delivery, multi-session readiness, CLUB/PERSONAL Recipe ownership, publication/moderation, ordered Recipe variants per Dish, project-level generation modes with persisted assignment Recipe snapshots, append-only actor-aware audit, complete consolidated Russian Project PDF/XLSX exports, and one centralized no-exceptions alcohol policy across Product, Recipe, Dish, API, and CSV import paths.

Alembic head is `h10021`. Release tag `v0.1.0` is created only by the Final Release Readiness workflow after all required workflows pass on the exact merged `main` SHA.

## Quick start

Use the production-like release stack for an operator installation:

```bash
git checkout v0.1.0
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

Frontend API calls use the same origin under `/api/v1` and are proxied by the frontend Nginx container to Backend. Browser-facing code must not hardcode `localhost:8000`, because `localhost` would refer to the user's computer rather than the TourHub server.

Database migrations run through the Backend container entrypoint. PostgreSQL data is stored in the `postgres18_cluster_data` named Docker volume. The release stack does not publish PostgreSQL or Redis ports.

The default `docker-compose.yml` remains the development-oriented stack with source bind mounts and infrastructure ports.

## Operator documentation

- [Deployment checklist](docs/DEPLOYMENT_CHECKLIST.md) — release prerequisites, secrets, backup, upgrade, health, LAN, smoke, rollback, and sign-off;
- [Installation runbook](docs/INSTALLATION.md) — first startup, health checks, LAN access, backups, and routine operations;
- [Docker release runtime](docs/DOCKER_RELEASE.md) — immutable images, release Compose, health contract, internal services, and automated runtime validation;
- [Update and recovery runbook](docs/UPDATING.md) — backup-first update, explicit migrations, verification, restore, and rollback boundaries;
- [v0.1.0 release notes](docs/releases/v0.1.0.md) — released scope, verification, upgrade, rollback, and deferred capabilities.

Create a release-stack host-side PostgreSQL custom-format backup:

```bash
COMPOSE_FILE=docker-compose.release.yml bash scripts/db/backup-tourhub.sh
```

Restore requires an explicit confirmation flag and leaves application services stopped:

```bash
COMPOSE_FILE=docker-compose.release.yml \
  bash scripts/db/restore-tourhub.sh backups/<dump-file>.dump --confirm
```

Production rollback is backup-based. Alembic downgrade is automated release verification evidence, not the normal operator rollback mechanism.

## Canonical documentation

Use these documents for current decisions:

- [`docs/PRODUCT_SPEC.md`](docs/PRODUCT_SPEC.md) — approved full product target;
- [`docs/PRODUCT_ACCEPTANCE.md`](docs/PRODUCT_ACCEPTANCE.md) — accepted feature-frozen first-release scope;
- [`docs/product_acceptance_manifest.json`](docs/product_acceptance_manifest.json) — machine-readable Product Acceptance source of truth;
- [`docs/release_readiness_manifest.json`](docs/release_readiness_manifest.json) — machine-readable v0.1.0 release contract;
- [`docs/DEPLOYMENT_CHECKLIST.md`](docs/DEPLOYMENT_CHECKLIST.md) — operator release sign-off;
- [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) — verified implemented and release state;
- [`docs/CURRENT_ROADMAP.md`](docs/CURRENT_ROADMAP.md) — delivered sequence and post-release selection boundary;
- [`docs/ARCHITECTURE_CURRENT.md`](docs/ARCHITECTURE_CURRENT.md) — current architecture boundaries;
- [`docs/DOMAIN_CURRENT.md`](docs/DOMAIN_CURRENT.md) — current persisted domain;
- [`docs/TECH_DEBT.md`](docs/TECH_DEBT.md) — deferred and decision-gated work;
- [`docs/tasks/TASKS.md`](docs/tasks/TASKS.md) — active and closed task index.

Current documents, accepted ADRs, Product Acceptance, and Release Readiness override historical files under archive or legacy directories.

## Quality and release gates

GitHub Actions enforce:

- full Backend tests, selected Ruff and strict mypy baselines, and Alembic single-head validation;
- Frontend tests, moderate-severity dependency audit, production build, and browser acceptance;
- dedicated Product Acceptance manifest, selected Backend API/migration, and six critical Chrome scenarios;
- guided desktop/mobile create-to-ZIP release acceptance;
- PostgreSQL 18 backup/restore smoke testing;
- operator runbook and script validation;
- production-like Docker image build and clean runtime smoke testing;
- final PostgreSQL 18 `h10020 → h10021 → h10020 → h10021` verification;
- exact-head merged-`main` evidence before lightweight tag `v0.1.0` is created.

## Development rules

- one logical change per task and squash commit;
- migrations must keep exactly one Alembic head;
- Backend owns calculations, import validation, transactions, identity, authorization, lifecycle, generation, audit, document content, and catalogue policies;
- Frontend owns presentation, navigation, form state, and API integration;
- Frontend features use the shared API client and do not hardcode browser-visible service origins;
- the v0.1.0 baseline is feature frozen and may not be expanded without an explicit Product Owner decision and a new post-release task;
- documentation must remain synchronized with product, domain, architecture, persistence, operations, and release state.
