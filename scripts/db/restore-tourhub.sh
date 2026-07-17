#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash scripts/db/restore-tourhub.sh DUMP_FILE --confirm

Restores the TourHub PostgreSQL database from a custom-format dump.
The backend and frontend are stopped and are not restarted automatically.
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ $# -ne 2 || "$2" != "--confirm" ]]; then
  usage >&2
  exit 2
fi

if [[ ! -r "$1" || ! -s "$1" ]]; then
  printf 'Restore failed: dump file is missing, unreadable, or empty: %s\n' "$1" >&2
  exit 1
fi

dump_directory="$(cd "$(dirname "$1")" && pwd)"
dump_file="${dump_directory}/$(basename "$1")"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

docker compose up -d postgres

for _ in $(seq 1 30); do
  if docker compose exec -T postgres \
    pg_isready --username=tourhub --dbname=postgres >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

docker compose exec -T postgres \
  pg_isready --username=tourhub --dbname=postgres >/dev/null

docker compose stop backend frontend >/dev/null

existing_database="$(
  docker compose exec -T postgres \
    psql \
    --username=tourhub \
    --dbname=postgres \
    --tuples-only \
    --no-align \
    --command="SELECT 1 FROM pg_database WHERE datname = 'tourhub';"
)"

if [[ "$existing_database" == "1" ]]; then
  timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
  safety_backup="backups/pre-restore-${timestamp}.dump"
  bash scripts/db/backup-tourhub.sh "$safety_backup"
  printf 'Pre-restore safety backup: %s\n' "$safety_backup"
fi

docker compose exec -T postgres \
  dropdb --username=tourhub --if-exists --force tourhub

docker compose exec -T postgres \
  createdb --username=tourhub --owner=tourhub tourhub

docker compose exec -T postgres \
  pg_restore \
  --username=tourhub \
  --dbname=tourhub \
  --no-owner \
  --exit-on-error < "$dump_file"

printf 'TourHub database restored from: %s\n' "$dump_file"
printf 'Application services remain stopped. Select the intended code version, rebuild, and start them explicitly.\n'
