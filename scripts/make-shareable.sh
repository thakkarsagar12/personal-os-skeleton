#!/usr/bin/env bash
# Adopter tool: verify this tree is safe to share.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
echo "Running privacy scan on $ROOT ..."
if bash "$HERE/scan-core.sh" "$ROOT"; then
  echo "OK — safe to share."
  exit 0
fi
cat <<'MSG'

BLOCKED. Personal data or denylisted paths detected above.
Remove the flagged content from your files, or if this is a known-safe
pattern, update scripts/identifiers.txt. Never commit docker-data/ or
memory/. See PRIVACY.md.
MSG
exit 1
