#!/bin/sh
set -eu

LOCK_HASH_FILE="node_modules/.tourhub-package-lock.sha256"
CURRENT_LOCK_HASH="$(sha256sum package-lock.json | awk '{print $1}')"
INSTALLED_LOCK_HASH=""

if [ -f "$LOCK_HASH_FILE" ]; then
  INSTALLED_LOCK_HASH="$(cat "$LOCK_HASH_FILE")"
fi

if [ ! -d node_modules ] || [ "$CURRENT_LOCK_HASH" != "$INSTALLED_LOCK_HASH" ]; then
  echo "Synchronizing frontend dependencies with package-lock.json..."
  npm ci
  printf '%s' "$CURRENT_LOCK_HASH" > "$LOCK_HASH_FILE"
fi

exec npm run dev -- --host
