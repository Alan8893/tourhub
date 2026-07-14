#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  printf 'Usage: %s <backup.dump>\n' "$0" >&2
  exit 2
fi

backup_path="$1"
container_path="/tmp/tourhub-restore.dump"

if [[ ! -f "$backup_path" ]]; then
  printf 'Backup file not found: %s\n' "$backup_path" >&2
  exit 2
fi

docker compose cp "$backup_path" "postgres:$container_path"

docker compose exec -T postgres \
  pg_restore --username=tourhub --dbname=tourhub --clean --if-exists --no-owner "$container_path"

docker compose exec -T postgres rm -f "$container_path"

printf 'PostgreSQL backup restored from: %s\n' "$backup_path"
