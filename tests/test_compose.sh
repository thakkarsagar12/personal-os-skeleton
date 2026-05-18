D="$(dirname "${BASH_SOURCE[0]}")/.."
assert_ok test -f "$D/docker-compose.yml"
assert_ok test -f "$D/.env.example"
# no hard-coded secrets / personal ports
assert_err grep -qiE 'thakkar|sagar|50011|50012' "$D/docker-compose.yml"
assert_ok grep -q 'POSTGRES_PORT' "$D/.env.example"
assert_ok grep -q '\${' "$D/docker-compose.yml"
