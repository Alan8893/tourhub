# PostgreSQL backup and restore

TourHub stores persistent application data in the PostgreSQL 18 Docker volume. Backups must be copied outside that volume before upgrades, destructive maintenance, or host migration.

## Preconditions

Start PostgreSQL and wait for its healthcheck:

```bash
docker compose up -d postgres
docker compose ps postgres
```

The scripts use the Compose service name `postgres` and the development database credentials declared in `docker-compose.yml`.

## Create a backup

### PowerShell

```powershell
./scripts/db/postgres-backup.ps1
```

Optional destination:

```powershell
./scripts/db/postgres-backup.ps1 -BackupPath backups/tourhub-before-upgrade.dump
```

### Bash

```bash
./scripts/db/postgres-backup.sh
```

Optional destination:

```bash
./scripts/db/postgres-backup.sh backups/tourhub-before-upgrade.dump
```

The scripts create a PostgreSQL custom-format dump inside the container and copy it to the host with `docker compose cp`. This avoids binary-redirection corruption on Windows.

Store backup files outside the repository and outside the PostgreSQL Docker volume. The local `backups/` directory is ignored by Git.

## Restore a backup

Restoration replaces database objects present in the dump. Stop backend traffic before restoring:

```bash
docker compose stop backend
```

### PowerShell

```powershell
./scripts/db/postgres-restore.ps1 -BackupPath backups/tourhub-before-upgrade.dump
```

### Bash

```bash
./scripts/db/postgres-restore.sh backups/tourhub-before-upgrade.dump
```

Restart the backend after a successful restore:

```bash
docker compose up -d backend
```

The backend startup applies any migrations newer than the restored backup before starting Uvicorn.

## Verification

Check service health and a representative API flow after restoration:

```bash
docker compose ps
docker compose logs --tail=100 backend
```

CI runs `scripts/db/verify-postgres-backup-restore.sh`. The smoke test starts PostgreSQL 18, creates a source database with a marker row, writes a custom-format dump, restores it into a separate database, and verifies the restored value.

## Failure handling

- Do not delete the previous backup until the restored application has been verified.
- A failed restore must not be followed by manual schema edits. Preserve logs and retry from a known-good dump.
- Never commit dumps: they can contain club and user data.
- Production credentials must not be hard-coded into these development scripts; production deployment must inject its own database configuration.
