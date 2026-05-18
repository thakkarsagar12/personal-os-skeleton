#!/usr/bin/env bash
# Test: allowlist manifest + build-from-source copier
D="$(dirname "${BASH_SOURCE[0]}")/.."
assert_ok test -f "$D/tools/manifest.tsv"
# manifest only references owned, non-personal source paths
assert_err grep -qiE 'Astrology-Valut|family/|career/|secrets|vault|behavior-log' "$D/tools/manifest.tsv"
# every manifest target exists after build
while IFS=$'\t' read -r s t mode; do
  case "$s" in ''|\#*) continue;; esac
  assert_ok test -f "$D/$t"
done < "$D/tools/manifest.tsv"
