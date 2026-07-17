# TourHub Update and Recovery Runbook

Every update is backup-first. Do not delete the PostgreSQL volume to solve an application or migration problem.

## Before updating

Record the currently deployed revision:

```bash
git rev-parse HEAD
```

Check that the installation is healthy:

```bash
docker compose ps
curl -fsS http://localhost:8000/api/v1/health
```

Create and retain a database backup outside the server:

```bash
bash scripts/db/backup-tourhub.sh
```

The command must finish with a non-empty `.dump` file before you continue.

## Update to the latest approved revision

For an installation tracking an approved branch:

```bash
git fetch --prune --tags
git pull --ff-only
```

For a pinned release, replace the pull command with:

```bash
git checkout <release-tag-or-commit>
```

Build the application images before changing the running application:

```bash
docker compose build --pull backend frontend
```

Start only the infrastructure services:

```bash
docker compose up -d postgres redis
```

Apply migrations explicitly. The same migration command is also executed by the backend entrypoint, but running it here makes a migration failure visible before the application is restarted:

```bash
docker compose run --rm --entrypoint alembic backend upgrade head
```

Start or replace the application services:

```bash
docker compose up -d backend frontend
```

## Verify the update

```bash
docker compose ps
docker compose exec -T backend alembic current
curl -fsS http://localhost:8000/api/v1/health
docker compose logs --tail=100 backend frontend
```

Open `http://localhost:5173` and verify the guided project flow and document download controls.

Keep the pre-update dump until the new version has been used successfully and another verified backup has been created.

## Recovery after an unsuccessful update

First collect diagnostics without deleting data:

```bash
docker compose ps
docker compose logs --tail=300 postgres backend frontend
```

If the failure is limited to application code and the database migration did not change persisted data, you may check out the previous revision, rebuild, and start it. When compatibility is uncertain, restore the pre-update backup instead of attempting an ad hoc Alembic downgrade.

### Restore a database backup

The restore command requires an explicit confirmation flag. It stops the frontend and backend, creates an additional safety backup when the current database exists, replaces the `tourhub` database, and leaves application services stopped:

```bash
bash scripts/db/restore-tourhub.sh backups/tourhub-YYYYMMDDTHHMMSSZ.dump --confirm
```

Then select the code revision that matches the restored data and rebuild:

```bash
git checkout <release-tag-or-commit>
docker compose build --pull backend frontend
docker compose up -d postgres redis
docker compose run --rm --entrypoint alembic backend upgrade head
docker compose up -d backend frontend
```

Repeat the health and migration checks from the verification section.

## Rollback boundaries

- Do not use `docker compose down --volumes` as an update or rollback step.
- Do not run `alembic downgrade` in production unless a release-specific rollback procedure explicitly requires and validates it.
- Restoring a database dump replaces data created after that dump. The restore script creates a `pre-restore-*.dump` safety copy when possible.
- PostgreSQL major-version upgrades are separate infrastructure work. Do not reuse the application update procedure to replace the PostgreSQL 18 data directory with another major version.
- Club users should stop editing projects during backup, migration, and restore windows.

## Backup inspection

List a dump without restoring it:

```bash
docker compose exec -T postgres pg_restore --list < backups/tourhub-YYYYMMDDTHHMMSSZ.dump | head
```

A successful listing confirms that PostgreSQL can read the custom-format archive; it does not replace a full restore test.
