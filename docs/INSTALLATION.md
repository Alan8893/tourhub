# TourHub Installation Runbook

TourHub is a local single-club application. Deploy it on a trusted computer or server inside the club network. The current Docker Compose file publishes PostgreSQL and Redis ports and is not intended for direct internet exposure.

## Prerequisites

- Git;
- Docker Engine with Docker Compose v2, or Docker Desktop;
- at least 4 GB of available memory;
- free host ports `5173`, `8000`, `5432`, and `6379`;
- Bash for the provided backup and restore scripts. On Windows, use WSL or Git Bash.

Verify the tools:

```bash
git --version
docker --version
docker compose version
```

## Install

Clone the repository and select the approved release tag or commit:

```bash
git clone https://github.com/Alan8893/tourhub.git
cd tourhub
git checkout <release-tag-or-commit>
```

Build and start all services:

```bash
docker compose up -d --build
```

The backend entrypoint waits for PostgreSQL through Compose dependencies, applies `alembic upgrade head`, and then starts the API. The current migration head is `h10007`.

## Verify the installation

Check container state:

```bash
docker compose ps
```

Check the backend health endpoint:

```bash
curl -fsS http://localhost:8000/api/v1/health
```

Expected response:

```json
{"status":"healthy"}
```

Confirm the applied database revision and inspect startup logs:

```bash
docker compose exec -T backend alembic current
docker compose logs --tail=100 backend
```

Open:

- TourHub: `http://localhost:5173`;
- API documentation: `http://localhost:8000/docs`.

From another computer on the same trusted network, use the server address:

```text
http://<server-ip>:5173
```

Allow inbound TCP `5173` in the server firewall only for the trusted network. Do not expose `5432`, `6379`, or `8000` to the public internet.

## Create the first backup

After completing the initial club setup, create a host-side PostgreSQL custom-format dump:

```bash
bash scripts/db/backup-tourhub.sh
```

Backups are written to `backups/` by default. Copy important dumps to storage outside the TourHub server.

## Routine operations

View logs:

```bash
docker compose logs -f backend frontend
```

Restart the application without deleting data:

```bash
docker compose restart backend frontend
```

Stop all containers while preserving PostgreSQL data:

```bash
docker compose down
```

Start them again:

```bash
docker compose up -d
```

PostgreSQL data is stored in the named volume `postgres18_cluster_data`. Never run `docker compose down --volumes` unless you intentionally want to delete the database and already have a verified backup.

## Troubleshooting

If the backend does not become healthy:

```bash
docker compose ps
docker compose logs --tail=200 postgres backend
```

If a published port is already in use, stop the conflicting service or change the host-side port mapping in `docker-compose.yml` before starting TourHub.

If migration startup fails, do not repeatedly recreate containers or delete the database volume. Preserve the logs and follow the backup-first recovery procedure in [UPDATING.md](UPDATING.md).
