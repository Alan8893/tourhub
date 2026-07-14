#!/usr/bin/env bash
set -euo pipefail

source_db="tourhub_backup_source"
target_db="tourhub_backup_target"
dump_path="/tmp/tourhub-backup-smoke.dump"

cleanup() {
  docker compose exec -T postgres dropdb --username=tourhub --if-exists "$source_db" >/dev/null 2>&1 || true
  docker compose exec -T postgres dropdb --username=tourhub --if-exists "$target_db" >/dev/null 2>&1 || true
  docker compose exec -T postgres rm -f "$dump_path" >/dev/null 2>&1 || true
  docker compose down --volumes >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker compose up -d postgres

for _ in $(seq 1 30); do
  if docker compose exec -T postgres pg_isready --username=tourhub --dbname=tourhub >/dev/null; then
    break
  fi
  sleep 1
done

docker compose exec -T postgres createdb --username=tourhub "$source_db"
docker compose exec -T postgres psql --username=tourhub --dbname="$source_db" --set=ON_ERROR_STOP=1 \
  --command="CREATE TABLE backup_probe (value text NOT NULL); INSERT INTO backup_probe VALUES ('tourhub-backup-ok');"

docker compose exec -T postgres pg_dump --username=tourhub --dbname="$source_db" --format=custom --file="$dump_path"
docker compose exec -T postgres createdb --username=tourhub "$target_db"
docker compose exec -T postgres pg_restore --username=tourhub --dbname="$target_db" --no-owner "$dump_path"

restored_value="$(docker compose exec -T postgres psql --username=tourhub --dbname="$target_db" --tuples-only --no-align --command='SELECT value FROM backup_probe;')"
test "$restored_value" = "tourhub-backup-ok"

printf 'PostgreSQL backup/restore smoke test passed.\n'
