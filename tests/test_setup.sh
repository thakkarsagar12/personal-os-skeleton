#!/usr/bin/env bash
D="$(dirname "${BASH_SOURCE[0]}")/.."
out="$(DRY_RUN=1 bash "$D/setup.sh" 2>&1)"
assert_eq "$?" "0" "setup dry-run exit"
assert_ok grep -q 'core.hooksPath' <<<"$out"
assert_ok grep -q 'docker compose' <<<"$out"
assert_ok grep -qi 'init-os' <<<"$out"
