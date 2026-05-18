#!/usr/bin/env bash
# Usage: scan-core.sh <path> [identifiers-file]
# Exit 0 = clean, 1 = PII/denylisted path found, 2 = no identifiers file.
set -u
ROOT="${1:?path required}"
HERE="$(cd "$(dirname "$0")" && pwd)"
IDF="${2:-$HERE/identifiers.txt}"; [ -f "$IDF" ] || IDF="$HERE/identifiers.example.txt"
if [ ! -f "$IDF" ]; then echo "ERROR: no identifiers file" >&2; exit 2; fi
DENY="$HERE/denylist.txt"
rc=0

# 1. Denylisted paths present?
while IFS= read -r pat; do
  case "$pat" in ''|'#'*) continue;; esac
  hits="$(find "$ROOT" -path "*/${pat%/}*" 2>/dev/null)"
  if [ -n "$hits" ]; then
    echo "DENYLIST HIT: $pat"
    printf '%s\n' "$hits" | sed 's/^/  /'
    rc=1
  fi
done < "$DENY"

# 2. Identifier regexes in tracked text (binary matches also count as a hit)?
pat="$(grep -vE '^\s*#|^\s*$' "$IDF" | paste -sd'|' -)"
if [ -n "$pat" ]; then
  if grep -rnE "$pat" "$ROOT" \
       --exclude-dir=.git --exclude-dir=docker-data --exclude-dir=__pycache__ \
       --exclude='identifiers.txt' --exclude='identifiers.example.txt' \
       2>/dev/null | grep . ; then
    echo "IDENTIFIER HIT (above)"; rc=1
  fi
fi
[ "$rc" -eq 0 ] && echo "scan-core: CLEAN"
exit "$rc"
