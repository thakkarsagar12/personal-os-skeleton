#!/usr/bin/env bash
# Contract test for .claude/skills/init-os/SKILL.md
# Sourced by tests/run.sh — uses assert_ok / assert_err / assert_eq helpers.

F="$(dirname "${BASH_SOURCE[0]}")/../.claude/skills/init-os/SKILL.md"

# File exists
assert_ok test -f "$F"

# Frontmatter: name must be unquoted kebab-case matching directory
assert_ok grep -q '^name: init-os' "$F"

# One-question-at-a-time protocol stated explicitly
assert_ok grep -qi 'one question at a time' "$F"

# All required placeholder tokens documented
for tok in USER_NAME NORTH_STAR PILLAR_1 TRACK_NAME; do
  assert_ok grep -q "$tok" "$F"
done

# Rule module enabling documented
assert_ok grep -qi 'rule module' "$F"
