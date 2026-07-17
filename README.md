# TourHub

TourHub is a local ERP application for preparing tourist-club trips: projects, meal plans, dishes, recipes, shopping projections, equipment, branded Russian exports, and operational backup/restore.

One installation represents one tourist club. The current release is a single-user local MVP; invitation-only access, ownership, and moderation remain deferred.

## Quick start

```bash
docker compose up -d --build
curl -fsS http://localhost:8000/api/v1/health
```

After startup on the server:

- frontend: `http://localhost:5173`;
- backend API: `http://localhost:8000`;
- OpenAPI: `http://localhost:8000/docs`.

From another computer on the same trusted network, open:

```text
http://<server-ip>:5173
```

Frontend API calls use the same origin under `/api/v1` and are proxied to the backend container. Browser-facing frontend code must not hardcode `localhost:8000`, because `localhost` would refer to the user's computer rather than the TourHub server.

Database migrations run through the backend container entrypoint. PostgreSQL data is stored in the named Docker volume declared by `docker-compose.yml`.

## Operator documentation

- [Installation runbook](docs/INSTALLATION.md) — prerequisites, first startup, health checks, LAN access, backups, and routine operations;
- [Update and recovery runbook](docs/UPDATING.md) — backup-first update, explicit migrations, verification, restore, and rollback boundaries.

Create a host-side custom-format database backup:

```bash
bash scripts/db/backup-tourhub.sh
```

Restore requires an explicit confirmation flag and leaves application services stopped:

```bash
bash scripts/db/restore-tourhub.sh backups/<dump-file>.dump --confirm
```

## Canonical documentation

Use these documents for current decisions:

- [`docs/PRODUCT_SPEC.md`](docs/PRODUCT_SPEC.md) — approved full product target;
- [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) — verified implemented state;
- [`docs/CURRENT_ROADMAP.md`](docs/CURRENT_ROADMAP.md) — delivery order and selected release scope;
- [`docs/ARCHITECTURE_CURRENT.md`](docs/ARCHITECTURE_CURRENT.md) — current architecture boundaries;
- [`docs/DOMAIN_CURRENT.md`](docs/DOMAIN_CURRENT.md) — current persisted domain;
- [`docs/TECH_DEBT.md`](docs/TECH_DEBT.md) — active and completed debt;
- [`docs/tasks/TASKS.md`](docs/tasks/TASKS.md) — active and closed task index.

`PRODUCT_SPEC.md` describes the approved full target, including capabilities intentionally deferred from the current single-user release. `CURRENT_ROADMAP.md` and `PROJECT_STATUS.md` define what is implemented now and what is scheduled next. Current documents and accepted ADRs override historical files under archive or legacy directories.

## Quality gates

GitHub Actions currently enforce:

- backend tests;
- selected Ruff and strict mypy baselines;
- Alembic single-head validation;
- frontend tests, production build, and browser acceptance;
- guided desktop/mobile create-to-ZIP release acceptance;
- moderate-severity dependency audit;
- PostgreSQL 18 backup/restore smoke testing.

## Development rules

- one logical change per task and pull request;
- migrations must keep exactly one Alembic head;
- backend owns calculations, import validation, transaction boundaries, and future authorization decisions;
- frontend owns presentation, navigation, form state, and API integration;
- frontend features use the shared API client and do not hardcode browser-visible service origins;
- documentation must be synchronized when product, domain, architecture, persistence, or release scope changes.
