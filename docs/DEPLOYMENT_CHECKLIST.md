# TourHub v0.1.0 Deployment Checklist

Status: RELEASE CANDIDATE

Release tag: `v0.1.0`

Accepted Alembic head: `h10021`

This checklist is the operator sign-off contract for the first feature-frozen local single-club release. It complements `docs/INSTALLATION.md`, `docs/UPDATING.md`, `docs/DOCKER_RELEASE.md`, `docs/operations/POSTGRES_BACKUP_RESTORE.md`, and `docs/PRODUCT_ACCEPTANCE.md`.

## 1. Prerequisites

- [ ] Docker Engine and Docker Compose v2 are installed and healthy.
- [ ] The host has sufficient disk space for images, the PostgreSQL volume, and at least two backups.
- [ ] The operator has a maintenance window and local console access to the TourHub host.
- [ ] The checked-out source is exactly tag `v0.1.0` or the verified commit recorded by the final workflow.
- [ ] `docker compose -f docker-compose.release.yml config` completes successfully.
- [ ] No paid or externally hosted runtime service is required; the release stack contains only local `postgres`, `redis`, `backend`, and `frontend` services.

## 2. Configuration and secrets

- [ ] Set a non-default `TOURHUB_DB_PASSWORD` before first production use.
- [ ] Set `TOURHUB_AUTH_COOKIE_SECURE=true` when the deployment terminates HTTPS.
- [ ] Review `TOURHUB_AUTH_SESSION_TTL_DAYS` for the club operating policy.
- [ ] Configure `TOURHUB_SMTP_SECRET` only when saved SMTP settings require authentication.
- [ ] Confirm secrets are supplied through the deployment environment and are not committed to the repository.
- [ ] Confirm PostgreSQL and Redis remain internal and are not published by `docker-compose.release.yml`.

## 3. Backup

- [ ] Before any upgrade, create a custom-format backup:

```bash
COMPOSE_FILE=docker-compose.release.yml bash scripts/db/backup-tourhub.sh
```

- [ ] Record the generated dump path, timestamp, host, source commit/tag, and current Alembic revision.
- [ ] Verify the dump exists and is non-empty.
- [ ] Keep the backup outside the PostgreSQL named volume and retain it until post-upgrade sign-off.
- [ ] Periodically verify restore behavior with `scripts/db/restore-tourhub.sh` and the documented disposable-database procedure.

## 4. Upgrade and migration

- [ ] Read `docs/UPDATING.md` before changing the running stack.
- [ ] Fetch and check out the exact approved release tag:

```bash
git fetch --tags
git checkout v0.1.0
```

- [ ] Build and start the release stack:

```bash
docker compose -f docker-compose.release.yml up -d --build --wait
```

- [ ] Confirm the Backend entrypoint completed Alembic migration successfully.
- [ ] Confirm the database revision is exactly `h10021`:

```bash
docker compose -f docker-compose.release.yml exec -T backend alembic current
```

- [ ] Do not create or apply an unreviewed migration during release deployment.

## 5. Health verification

- [ ] Backend health succeeds:

```bash
curl -fsS http://localhost:8000/api/v1/health
```

- [ ] Frontend health succeeds:

```bash
curl -fsS http://localhost:5173/healthz
```

- [ ] `docker compose -f docker-compose.release.yml ps` shows all four services healthy or running as designed.
- [ ] Review Backend and PostgreSQL logs for migration, authentication, or persistence errors.
- [ ] Restart Backend and Frontend once and confirm health and persisted data remain intact.

## 6. LAN access

- [ ] From another trusted-LAN computer, open `http://<server-ip>:5173` or the approved HTTPS endpoint.
- [ ] Confirm frontend requests use the same-origin `/api/v1` proxy and do not target the client computer's `localhost:8000`.
- [ ] Confirm PostgreSQL and Redis are unreachable from the LAN.
- [ ] Confirm the configured firewall exposes only the approved frontend/backend or reverse-proxy ports.

## 7. Product smoke acceptance

- [ ] Complete Administrator bootstrap or sign in with an existing Administrator.
- [ ] Confirm invitation-only access and current role display.
- [ ] Open one existing Project and verify menu, shopping, equipment, readiness, and persisted reload state.
- [ ] Generate and download the complete Russian PDF, workbook, and coordinated ZIP.
- [ ] Confirm Product/Recipe/Dish alcohol-policy rejection remains HTTP 422 and archived historical records remain readable.
- [ ] Confirm `docs/PRODUCT_ACCEPTANCE.md` remains `FEATURE FROZEN` and no deferred capability was introduced.

## 8. Rollback boundary

Application rollback is backup-based after `h10021` has been applied to production data.

- [ ] Stop application services before restore.
- [ ] Use the exact pre-upgrade dump and explicit confirmation flag:

```bash
COMPOSE_FILE=docker-compose.release.yml \
  bash scripts/db/restore-tourhub.sh backups/<dump-file>.dump --confirm
```

- [ ] Restore the application code/tag that matches the restored database revision.
- [ ] Do not treat `alembic downgrade` as the normal production rollback mechanism.
- [ ] After restore, repeat health, revision, LAN, authentication, Project reload, and document smoke checks.

## 9. Operator sign-off

Record the following outside the application repository or in the club's approved operational log:

- release tag and exact commit SHA;
- deployment date/time and operator;
- host identifier;
- backup file and checksum/location;
- final Alembic revision `h10021`;
- health and smoke results;
- any accepted operational warning;
- final GO / NO-GO decision.

The deployment is complete only after every applicable checkbox is satisfied and the operator records **GO**.
