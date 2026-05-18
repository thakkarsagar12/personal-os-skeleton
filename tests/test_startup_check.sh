D="$(dirname "${BASH_SOURCE[0]}")/.."
out="$(python3 "$D/system/db/startup_check.py" 2>&1)"; rc=$?
assert_ok grep -qiE 'postgres|qdrant' <<<"$out"
# exits 0 even when infra down (it's a report, not a gate)
assert_eq "$rc" "0" "startup_check non-fatal"
