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
Edit scripts/identifiers.txt for YOUR identifiers, remove the
flagged content, and never commit docker-data/ or memory/.
See PRIVACY.md.
MSG
exit 1
