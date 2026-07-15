# TourHub

TourHub is a local ERP application for preparing tourist-club trips: projects, meal plans, dishes, recipes, shopping projections, exports, and operational backup/restore.

One installation represents one tourist club. The current delivery sequence completes the single-user club workflow before the approved multi-user access, ownership, and moderation phase.

## Local startup

```bash
docker compose up --build
```

After startup:

- frontend: `http://localhost:5173`;
- backend API: `http://localhost:8000`;
- OpenAPI: `http://localhost:8000/docs`.

Database migrations run through the backend container entrypoint. PostgreSQL data is stored in the named Docker volume declared by `compose.yml`.

## Canonical documentation

Use these documents for current decisions:

- [`docs/PRODUCT_SPEC.md`](docs/PRODUCT_SPEC.md) — approved full product target;
- [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) — verified implemented state;
- [`docs/CURRENT_ROADMAP.md`](docs/CURRENT_ROADMAP.md) — delivery order and selected release scope;
- [`docs/ARCHITECTURE_CURRENT.md`](docs/ARCHITECTURE_CURRENT.md) — current architecture boundaries;
- [`docs/DOMAIN_CURRENT.md`](docs/DOMAIN_CURRENT.md) — current persisted domain;
- [`docs/TECH_DEBT.md`](docs/TECH_DEBT.md) — active and completed debt;
- [`docs/tasks/TASKS.md`](docs/tasks/TASKS.md) — active and closed task index.

`PRODUCT_SPEC.md` describes the approved full target, including capabilities intentionally deferred from the current single-user release increment. `CURRENT_ROADMAP.md` and `PROJECT_STATUS.md` define what is implemented now and what is scheduled next. Current documents and accepted ADRs override historical files under archive or legacy directories.

## Quality gates

GitHub Actions currently enforce:

- backend tests;
- selected Ruff and strict mypy baselines;
- Alembic single-head validation;
- frontend tests and production build;
- moderate-severity dependency audit;
- PostgreSQL 18 backup/restore smoke testing.

## Development rules

- one logical change per task and pull request;
- migrations must keep exactly one Alembic head;
- backend owns calculations, import validation, transaction boundaries, and future authorization decisions;
- frontend owns presentation, navigation, form state, and API integration;
- documentation must be synchronized when product, domain, architecture, persistence, or release scope changes.
