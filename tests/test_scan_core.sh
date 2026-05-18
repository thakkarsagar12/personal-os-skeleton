TMP="$(dirname "${BASH_SOURCE[0]}")/.tmp"; rm -rf "$TMP"; mkdir -p "$TMP/clean" "$TMP/dirty"
# Synthetic identifiers only — no real PII anywhere in this repo.
IDS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/test-identifiers.txt"
echo "generic note, no personal data" > "$TMP/clean/a.md"
# Digits split across two literals so no 10-digit run appears in THIS
# source file (the product default ids has a [0-9]{10} regex). Runtime
# output is the full synthetic number, so the phone regex is still tested.
printf 'FIXTUREPII fixture@example.test 99999%s\n' '99999' > "$TMP/dirty/a.md"
SC="$(dirname "${BASH_SOURCE[0]}")/../scripts/scan-core.sh"
assert_ok  bash "$SC" "$TMP/clean" "$IDS"
assert_err bash "$SC" "$TMP/dirty" "$IDS"
mkdir -p "$TMP/deny/docker-data"; echo x > "$TMP/deny/docker-data/db"
assert_err bash "$SC" "$TMP/deny" "$IDS"

# Regression: binary file (null byte) containing an identifier must still be a hit.
mkdir -p "$TMP/bin"; printf '\x00FIXTUREPII\x01' > "$TMP/bin/blob.bin"
assert_err bash "$SC" "$TMP/bin" "$IDS"

# Regression: a 10-digit number must be caught by the POSIX phone regex.
mkdir -p "$TMP/phone"; printf 'call 99999%s today\n' '99999' > "$TMP/phone/a.md"
assert_err bash "$SC" "$TMP/phone" "$IDS"

# Regression: scan-core must NOT flag the active identifier file itself.
# (An adopter who edits scripts/identifiers.txt must not have that file
#  self-match on every scan. identifiers.txt + identifiers.example.txt
#  are both --exclude'd from the content grep.)
mkdir -p "$TMP/idfself/scripts"
echo "FIXTUREPII" > "$TMP/idfself/scripts/identifiers.txt"
echo "generic note, nothing personal" > "$TMP/idfself/other.md"
assert_ok bash "$SC" "$TMP/idfself" "$TMP/idfself/scripts/identifiers.txt"

# Cleanup: remove fixture artifacts (runtime files hold the full synthetic
# 10-digit string; leaving them on disk would trip a later whole-repo scan).
rm -rf "$TMP"
