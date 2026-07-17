#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash scripts/db/backup-tourhub.sh [OUTPUT_FILE]

Creates a PostgreSQL custom-format dump on the host.
Default: backups/tourhub-<UTC timestamp>.dump
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
output_file="${1:-backups/tourhub-${timestamp}.dump}"
temporary_file="${output_file}.tmp"

mkdir -p "$(dirname "$output_file")"
rm -f "$temporary_file"
trap 'rm -f "$temporary_file"' EXIT

docker compose exec -T postgres \
  pg_isready --username=tourhub --dbname=tourhub >/dev/null

docker compose exec -T postgres \
  pg_dump \
  --username=tourhub \
  --dbname=tourhub \
  --format=custom \
  --no-owner > "$temporary_file"

if [[ ! -s "$temporary_file" ]]; then
  printf 'Backup failed: dump is empty.\n' >&2
  exit 1
fi

mv "$temporary_file" "$output_file"
trap - EXIT

printf 'TourHub backup created: %s\n' "$output_file"
