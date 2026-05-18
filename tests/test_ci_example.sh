F="$(dirname "${BASH_SOURCE[0]}")/../.github/workflows/privacy.yml.example"
assert_ok test -f "$F"
assert_ok grep -q 'scan-core.sh' "$F"
assert_eq "${F##*.}" "example" "workflow must ship as .example"
