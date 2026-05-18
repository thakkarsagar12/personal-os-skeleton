#!/usr/bin/env bash
set -eu
DRY="${DRY_RUN:-0}"
run(){ echo "+ $*"; [ "$DRY" = 1 ] || "$@"; }

# Dependency checks — skipped in dry-run so DRY_RUN=1 always exits 0
if [ "$DRY" != 1 ]; then
  command -v docker  >/dev/null || { echo "Install Docker first.";  exit 1; }
  command -v python3 >/dev/null || { echo "Install python3 first."; exit 1; }
fi

run mkdir -p daily-ops/tasks daily-ops/reviews second-brain/inbox \
  second-brain/notes study/notes docker-data
[ -f .env ] || run cp .env.example .env
run git config core.hooksPath .githooks
run docker compose up -d
[ "$DRY" = 1 ] || sleep 5
run python3 system/db/startup_check.py || true
echo
echo "Infra up. Next: open Claude Code here and run /init-os to personalize."
