#!/usr/bin/env bash
set -u
PASS=0; FAIL=0
assert_eq()  { if [ "$1" = "$2" ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); echo "FAIL: $3 (got '$1' want '$2')"; fi; }
assert_ok()  { if "$@"; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); echo "FAIL: cmd ok: $*"; fi; }
assert_err() { if "$@"; then FAIL=$((FAIL+1)); echo "FAIL: cmd should fail: $*"; else PASS=$((PASS+1)); fi; }
for f in "$(dirname "$0")"/test_*.sh; do . "$f"; done
echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ]
