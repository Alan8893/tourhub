param(
    [string]$BackupPath = "backups/tourhub-$(Get-Date -AsUTC -Format 'yyyyMMddTHHmmssZ').dump"
)

$ErrorActionPreference = 'Stop'
$containerPath = '/tmp/tourhub-backup.dump'
$backupDirectory = Split-Path -Parent $BackupPath

if ($backupDirectory) {
    New-Item -ItemType Directory -Force -Path $backupDirectory | Out-Null
}

docker compose exec -T postgres pg_dump `
    --username=tourhub `
    --dbname=tourhub `
    --format=custom `
    --file=$containerPath

if ($LASTEXITCODE -ne 0) {
    throw 'pg_dump failed.'
}

docker compose cp "postgres:$containerPath" $BackupPath
if ($LASTEXITCODE -ne 0) {
    throw 'docker compose cp failed.'
}

docker compose exec -T postgres rm -f $containerPath
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to remove the temporary backup from the container.'
}

Write-Host "PostgreSQL backup created: $BackupPath"
