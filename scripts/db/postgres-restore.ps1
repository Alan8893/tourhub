param(
    [Parameter(Mandatory = $true)]
    [string]$BackupPath
)

$ErrorActionPreference = 'Stop'
$containerPath = '/tmp/tourhub-restore.dump'

if (-not (Test-Path -LiteralPath $BackupPath -PathType Leaf)) {
    throw "Backup file not found: $BackupPath"
}

docker compose cp $BackupPath "postgres:$containerPath"
if ($LASTEXITCODE -ne 0) {
    throw 'docker compose cp failed.'
}

docker compose exec -T postgres pg_restore `
    --username=tourhub `
    --dbname=tourhub `
    --clean `
    --if-exists `
    --no-owner `
    $containerPath

if ($LASTEXITCODE -ne 0) {
    throw 'pg_restore failed.'
}

docker compose exec -T postgres rm -f $containerPath
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to remove the temporary restore file from the container.'
}

Write-Host "PostgreSQL backup restored from: $BackupPath"
