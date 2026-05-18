#!/usr/bin/env bash
# Usage: scan-core.sh <path> [identifiers-file]
# Exit 0 = clean, 1 = PII/denylisted path found.
set -u
ROOT="${1:?path required}"
HERE="$(cd "$(dirname "$0")" && pwd)"
IDF="${2:-$HERE/identifiers.txt}"; [ -f "$IDF" ] || IDF="$HERE/identifiers.example.txt"
DENY="$HERE/denylist.txt"
rc=0

# 1. Denylisted paths present?
while IFS= read -r pat; do
  case "$pat" in ''|\#*) continue;; esac
  if find "$ROOT" -path "*/${pat%/}*" 2>/dev/null | grep -q .; then
    echo "DENYLIST HIT: $pat"; rc=1
  fi
done < "$DENY"

# 2. Identifier regexes in tracked text?
pat="$(grep -vE '^\s*#|^\s*$' "$IDF" | paste -sd'|' -)"
if [ -n "$pat" ]; then
  if grep -rInE "$pat" "$ROOT" \
       --exclude-dir=.git --exclude-dir=docker-data --exclude-dir=__pycache__ \
       2>/dev/null | grep -v '/identifiers.example.txt:' | grep . ; then
    echo "IDENTIFIER HIT (above)"; rc=1
  fi
fi
[ "$rc" -eq 0 ] && echo "scan-core: CLEAN"
exit "$rc"
