TMP="$(dirname "${BASH_SOURCE[0]}")/.tmp"; rm -rf "$TMP"; mkdir -p "$TMP/clean" "$TMP/dirty"
echo "generic note, no personal data" > "$TMP/clean/a.md"
echo "Sagar Prez NeoSoft thakkarsagar12@gmail.com" > "$TMP/dirty/a.md"
SC="$(dirname "${BASH_SOURCE[0]}")/../scripts/scan-core.sh"
assert_ok  bash "$SC" "$TMP/clean"
assert_err bash "$SC" "$TMP/dirty"
mkdir -p "$TMP/deny/docker-data"; echo x > "$TMP/deny/docker-data/db"
assert_err bash "$SC" "$TMP/deny"

# Regression: binary file (null byte) containing an identifier must still be a hit.
mkdir -p "$TMP/bin"; printf '\x00Sagar\x01' > "$TMP/bin/blob.bin"
assert_err bash "$SC" "$TMP/bin"

# Regression: a 10-digit number must be caught by the POSIX phone regex.
mkdir -p "$TMP/phone"; echo "call 9820153125 today" > "$TMP/phone/a.md"
assert_err bash "$SC" "$TMP/phone"
