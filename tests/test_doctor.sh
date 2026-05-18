D="$(dirname "${BASH_SOURCE[0]}")/.."
out="$(bash "$D/scripts/doctor.sh" 2>&1)"   # must run even if docker down
assert_ok grep -qE 'PASS|FAIL' <<<"$out"
assert_ok grep -qi 'docker' <<<"$out"
assert_ok grep -qi 'port'   <<<"$out"
