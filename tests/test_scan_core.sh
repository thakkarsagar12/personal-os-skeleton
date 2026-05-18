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

# Regression: scan-core must NOT flag the ACTIVE identifier file itself.
# (An adopter who edits scripts/identifiers.txt must not have that file
#  self-match on every scan. The active IDF is path-precisely suppressed
#  via `grep -vF -- "$IDF"`, NOT a broad basename --exclude.)
mkdir -p "$TMP/idfself/scripts"
echo "FIXTUREPII" > "$TMP/idfself/scripts/identifiers.txt"
echo "generic note, nothing personal" > "$TMP/idfself/other.md"
assert_ok bash "$SC" "$TMP/idfself" "$TMP/idfself/scripts/identifiers.txt"

# Regression (broad-exclude hole): a DIFFERENTLY-located file that merely
# happens to be NAMED identifiers.txt — but is NOT the active IDF — must
# still be scanned. A broad `--exclude='identifiers.txt'` would silently
# skip it and hide PII (hook fails open). Active IDF here is the unrelated
# test-identifiers.txt, so this nested identifiers.txt is just content.
mkdir -p "$TMP/broad/sub"
echo "FIXTUREPII" > "$TMP/broad/sub/identifiers.txt"
assert_err bash "$SC" "$TMP/broad" "$IDS"

# Regression: denylist bare-name ".env" must NOT match ".env.example"
# (exact basename match required — substring match is a false-positive).
mkdir -p "$TMP/envex"; echo "POSTGRES_PORT=5432" > "$TMP/envex/.env.example"
assert_ok bash "$SC" "$TMP/envex" "$IDS"

# Regression: denylist bare-name ".env" MUST match a real ".env" file.
mkdir -p "$TMP/envreal"; echo "SECRET=hunter2" > "$TMP/envreal/.env"
assert_err bash "$SC" "$TMP/envreal" "$IDS"

# Cleanup: remove fixture artifacts (runtime files hold the full synthetic
# 10-digit string; leaving them on disk would trip a later whole-repo scan).
rm -rf "$TMP"
