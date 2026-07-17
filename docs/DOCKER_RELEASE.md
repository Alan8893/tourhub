# TourHub Docker Release Runtime

`docker-compose.release.yml` is the production-like local deployment path for the single-club TourHub MVP. It is separate from the development-oriented `docker-compose.yml`.

## Runtime contract

The release stack:

- builds the backend image from `backend/Dockerfile`;
- builds the frontend with `frontend/Dockerfile.release` and serves the static Vite bundle through Nginx;
- proxies browser requests under `/api/` from the frontend container to the backend;
- publishes only frontend port `5173` and backend port `8000` by default;
- keeps PostgreSQL and Redis on the internal Compose network;
- runs backend migrations through the existing backend entrypoint;
- stores PostgreSQL data in the `postgres18_cluster_data` named volume;
- runs backend and frontend from image contents without application source bind mounts.

This is a trusted-LAN deployment path. It does not add TLS termination, public-internet hardening, external secret storage, or multi-tenant isolation.

## Configure

The default local database password is `tourhub`. Set a deployment-specific value before the first release start:

```bash
export TOURHUB_DB_PASSWORD='<url-encoded-password>'
```

The password is used in both PostgreSQL and the backend connection URL. Characters with special URL meaning must be percent-encoded.

Optional host-port overrides:

```bash
export TOURHUB_FRONTEND_PORT=5173
export TOURHUB_BACKEND_PORT=8000
```

Keep the same database password for subsequent starts of the existing volume. Changing only the environment value does not rewrite credentials already stored in PostgreSQL.

## Build and start

Render the effective configuration before startup:

```bash
docker compose -f docker-compose.release.yml config
```

Build current images and pull current base images:

```bash
docker compose -f docker-compose.release.yml build --pull
```

Start the stack and wait for health checks:

```bash
docker compose -f docker-compose.release.yml up -d --wait --wait-timeout 180
```

Inspect state and logs:

```bash
docker compose -f docker-compose.release.yml ps
docker compose -f docker-compose.release.yml logs --tail=100 backend frontend
```

## Verify

Backend health:

```bash
curl -fsS http://localhost:8000/api/v1/health
```

Frontend health and same-origin API proxy:

```bash
curl -fsS http://localhost:5173/healthz
curl -fsS http://localhost:5173/api/v1/health
```

Expected API health response:

```json
{"status":"healthy"}
```

Verify the applied migration revision:

```bash
docker compose -f docker-compose.release.yml exec -T backend alembic current
```

Open TourHub at `http://localhost:5173` or `http://<server-ip>:5173` on the trusted LAN.

## Backup and restore

The existing scripts use Docker Compose service names and support the release file through the standard `COMPOSE_FILE` environment variable.

Create a backup:

```bash
COMPOSE_FILE=docker-compose.release.yml bash scripts/db/backup-tourhub.sh
```

Restore a verified dump:

```bash
COMPOSE_FILE=docker-compose.release.yml \
  bash scripts/db/restore-tourhub.sh backups/<dump-file>.dump --confirm
```

The restore command creates a pre-restore safety dump when a current database exists and leaves backend/frontend stopped. Rebuild and start the intended release explicitly after verification.

## Stop safely

Stop containers while preserving PostgreSQL data:

```bash
docker compose -f docker-compose.release.yml down
```

Do not use `down --volumes` for an operational installation. That option is used only by the disposable GitHub Actions clean-environment test and deletes the PostgreSQL volume for that isolated CI project.

Follow [UPDATING.md](UPDATING.md) for backup-first updates and recovery boundaries.

## Automated validation

The `Docker Release Runtime` workflow verifies on every pull request that:

- the release Compose contract renders and contains no application bind mounts;
- PostgreSQL and Redis publish no host ports;
- backend and frontend images build from clean inputs;
- a disposable stack reaches healthy state;
- Nginx serves the built frontend and proxies API requests;
- a project can be created and remains persisted after application container restart;
- the database is at the current Alembic head;
- failure logs are captured and the disposable stack is always removed.
