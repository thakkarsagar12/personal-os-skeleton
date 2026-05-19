# Test: a privacy CI workflow ships ACTIVE under .github/workflows/.
# Name-agnostic by design — asserts the REAL guarantee (the workflow
# exists, runs scan-core.sh, triggers on push/pull_request), NOT a
# specific filename. An inert `*.yml.example` would be a regression:
# GitHub Actions does not run `.example` files, so this test must NOT
# accept one as the active gate.

_WF_DIR="$(dirname "${BASH_SOURCE[0]}")/../.github/workflows"

# Exactly one privacy workflow file, matched by glob (name-agnostic).
_WF="$(ls "$_WF_DIR"/privacy*.y*ml* 2>/dev/null | head -1)"
assert_ok test -n "$_WF"
assert_ok test -f "$_WF"

# It must be an ACTIVE workflow, not an inert `.example` variant.
assert_err test "${_WF##*.}" = "example"

# It must reference the scanner.
assert_ok grep -q 'scan-core.sh' "$_WF"

# It must trigger on push and pull_request.
assert_ok grep -qE '\bpush\b' "$_WF"
assert_ok grep -qE '\bpull_request\b' "$_WF"
