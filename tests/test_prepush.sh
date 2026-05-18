#!/usr/bin/env bash
# Test: pre-push hook blocks PII-containing commits; allows clean ones.
# This file is sourced by tests/run.sh — use ${BASH_SOURCE[0]} for paths.

_TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_SKEL_ROOT="$(cd "$_TESTS_DIR/.." && pwd)"
_TMP_PP="$_TESTS_DIR/.tmp/prepush"

# Clean up from any prior run
rm -rf "$_TMP_PP"
mkdir -p "$_TMP_PP"

# Create a bare repo as the push target (absolute path, outside the clone)
_BARE="$_TMP_PP/origin.git"
git init --bare -q "$_BARE"

# Create a temp working clone (NOT inside the skeleton tree)
_CLONE="$_TMP_PP/clone"
git init -q "$_CLONE"
git -C "$_CLONE" config user.email "test@test.local"
git -C "$_CLONE" config user.name "test"

# Copy scripts/ and .githooks/ from skeleton into the clone
cp -R "$_SKEL_ROOT/scripts" "$_CLONE/scripts"
mkdir -p "$_CLONE/.githooks"
# .githooks/pre-push may not exist yet at Step 1 (TDD red phase) — copy if present
if [ -f "$_SKEL_ROOT/.githooks/pre-push" ]; then
  cp "$_SKEL_ROOT/.githooks/pre-push" "$_CLONE/.githooks/pre-push"
fi

# The hook calls make-shareable.sh -> scan-core.sh with the DEFAULT
# identifier path. Add a SYNTHETIC token to the temp clone's
# scripts/identifiers.txt (this file lives only in the temp clone,
# never in the skeleton tree) so the hook catches our fixture token.
echo "FIXTUREPII" > "$_CLONE/scripts/identifiers.txt"

# Point git at the hooks dir and the bare remote
git -C "$_CLONE" config core.hooksPath .githooks
git -C "$_CLONE" remote add origin "$_BARE"

# --- Test A: clean file pushes OK ---
echo "generic skeleton note, no personal data" > "$_CLONE/README.md"
git -C "$_CLONE" add README.md
git -C "$_CLONE" commit -q -m "clean commit"
assert_ok git -C "$_CLONE" push -q origin HEAD

# --- Test B: file containing synthetic PII is blocked by the pre-push hook ---
echo "FIXTUREPII synthetic employee record" > "$_CLONE/private.md"
git -C "$_CLONE" add private.md
git -C "$_CLONE" commit -q -m "dirty commit"
assert_err git -C "$_CLONE" push -q origin HEAD

# --- Test C: hook fails CLOSED when the scanner script is absent ---
# Remove the dirty file first so the ONLY factor under test is the
# missing scanner, then delete make-shareable.sh. The hook execs a
# now-missing file -> non-zero exit -> push must still be blocked.
git -C "$_CLONE" rm -q private.md
git -C "$_CLONE" commit -q -m "drop dirty file"
rm "$_CLONE/scripts/make-shareable.sh"
echo "scanner intentionally removed" >> "$_CLONE/README.md"
git -C "$_CLONE" add README.md
git -C "$_CLONE" commit -q -m "hook script removed"
assert_err git -C "$_CLONE" push -q origin HEAD

# Cleanup
rm -rf "$_TMP_PP"
