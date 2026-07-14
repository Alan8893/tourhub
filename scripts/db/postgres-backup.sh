#!/usr/bin/env bash
set -euo pipefail

backup_path="${1:-backups/tourhub-$(date -u +%Y%m%dT%H%M%SZ).dump}"
container_path="/tmp/tourhub-backup.dump"

mkdir -p "$(dirname "$backup_path")"

docker compose exec -T postgres \
  pg_dump --username=tourhub --dbname=tourhub --format=custom --file="$container_path"

docker compose cp "postgres:$container_path" "$backup_path"
docker compose exec -T postgres rm -f "$container_path"

printf 'PostgreSQL backup created: %s\n' "$backup_path"
