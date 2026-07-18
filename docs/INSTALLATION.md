# TourHub Installation Runbook

TourHub is a local single-club application. Deploy it on a trusted computer or server inside the club network. Use `docker-compose.release.yml` for the operator installation path. PostgreSQL and Redis remain internal to the release Compose network and must not be exposed directly to the public internet.

## Prerequisites

- Git;
- Docker Engine with Docker Compose v2, or Docker Desktop;
- at least 4 GB of available memory;
- free host ports `5173` and `8000`;
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

Set a deployment-specific database password before the first start. Characters with special URL meaning must be percent-encoded because the same value is used in the backend PostgreSQL URL:

```bash
export TOURHUB_DB_PASSWORD='<url-encoded-password>'
```

Keep this value in the server's protected environment configuration. Use the same password on future starts of the existing PostgreSQL volume.

The System Settings mail section recognizes an optional external SMTP value:

```bash
export TOURHUB_SMTP_SECRET='<smtp-value>'
```

Keep this value only in protected host environment configuration. The current mail-boundary implementation reports whether it is configured, but does not connect to SMTP, verify it, or send messages. Do not put the value in PostgreSQL, normal API requests, logs, screenshots, or unencrypted configuration exports.

Render the effective release configuration:

```bash
docker compose -f docker-compose.release.yml config
```

Build and start all services, then wait for health checks:

```bash
docker compose -f docker-compose.release.yml \
  up -d --build --wait --wait-timeout 180
```

The backend entrypoint waits for healthy PostgreSQL and Redis services, applies `alembic upgrade head`, and then starts the API. The current migration head is `h10015`. The frontend image contains a compiled Vite bundle served by Nginx; it does not mount application source code.

## Verify the installation

Check container state:

```bash
docker compose -f docker-compose.release.yml ps
```

Check the backend health endpoint:

```bash
curl -fsS http://localhost:8000/api/v1/health
```

Check the frontend container and its same-origin backend proxy:

```bash
curl -fsS http://localhost:5173/healthz
curl -fsS http://localhost:5173/api/v1/health
```

Expected API response:

```json
{"status":"healthy"}
```

Confirm the applied database revision and inspect startup logs:

```bash
docker compose -f docker-compose.release.yml exec -T backend alembic current
docker compose -f docker-compose.release.yml logs --tail=100 backend frontend
```

Open:

- TourHub: `http://localhost:5173`;
- API documentation: `http://localhost:8000/docs`.

### Create the first Administrator

On a new installation TourHub opens the one-time **«Создание первого администратора»** form. Enter the Administrator name, email, and a password of at least 12 characters.

- TourHub has no default application password;
- the first account is always an Administrator;
- the bootstrap form disappears after the first user is created;
- repeated bootstrap attempts are rejected by Backend;
- keep the Administrator password in the club's approved password manager;
- do not place the application password in Compose files, `.env` committed to Git, logs, screenshots, or support messages.

After creation, verify that the header shows the Administrator name, `/settings` opens, logout returns to the login form, and the same account can sign in again.

From another computer on the same trusted network, use the server address:

```text
http://<server-ip>:5173
```

Allow inbound TCP `5173` in the server firewall only for the trusted network. Backend port `8000` is published for operator diagnostics and OpenAPI access; do not expose it to the public internet. PostgreSQL and Redis publish no host ports in the release stack.

## Create the first backup

After completing the initial club setup and Administrator bootstrap, create a host-side PostgreSQL custom-format dump against the release stack:

```bash
COMPOSE_FILE=docker-compose.release.yml bash scripts/db/backup-tourhub.sh
```

Backups are written to `backups/` by default. Copy important dumps to storage outside the TourHub server.

## Routine operations

View logs:

```bash
docker compose -f docker-compose.release.yml logs -f backend frontend
```

Restart the application without restarting PostgreSQL or deleting data:

```bash
docker compose -f docker-compose.release.yml restart backend frontend
docker compose -f docker-compose.release.yml up -d --wait --wait-timeout 120
```

Stop all containers while preserving PostgreSQL data:

```bash
docker compose -f docker-compose.release.yml down
```

Start them again:

```bash
docker compose -f docker-compose.release.yml up -d --wait --wait-timeout 180
```

PostgreSQL data is stored in the named volume `postgres18_cluster_data`. Never run `docker compose -f docker-compose.release.yml down --volumes` for an operational installation unless you intentionally want to delete the database and already have a verified backup.

The default `docker-compose.yml` is the development stack. It uses source bind mounts and publishes PostgreSQL and Redis ports; do not substitute it for the release path without understanding those differences.

## Troubleshooting

If the backend does not become healthy:

```bash
docker compose -f docker-compose.release.yml ps
docker compose -f docker-compose.release.yml logs --tail=200 postgres redis backend
```

If a published application port is already in use, set a host-side override before startup:

```bash
export TOURHUB_FRONTEND_PORT=15173
export TOURHUB_BACKEND_PORT=18000
```

If migration startup fails, do not repeatedly recreate containers or delete the database volume. Preserve the logs and follow the backup-first recovery procedure in [UPDATING.md](UPDATING.md).

See [DOCKER_RELEASE.md](DOCKER_RELEASE.md) for the full release image, network, health, and CI runtime contract.
