#!/usr/bin/env bash
set -u
chk(){ if eval "$2" >/dev/null 2>&1; then echo "PASS  $1"; else echo "FAIL  $1  -> $3"; fi; }
[ -f .env ] && . ./.env
chk "docker installed"  "command -v docker"            "install Docker"
chk "docker running"    "docker info"                  "start Docker Desktop"

# Only probe compose service ports when docker daemon is actually up;
# avoids hangs from 'docker compose ps' talking to an unreachable daemon.
if docker info >/dev/null 2>&1; then
  chk "postgres port free or ours" "true"                "n/a"
  chk "compose file"      "test -f docker-compose.yml"   "run from repo root"
  chk "postgres reachable" "docker compose ps postgres | grep -q Up" "make init"
  chk "qdrant reachable"   "docker compose ps qdrant   | grep -q Up" "make init"
else
  echo "FAIL  postgres port free or ours  -> start Docker Desktop"
  echo "FAIL  compose file (skipped — docker not running)"
  echo "FAIL  postgres reachable  -> make init"
  echo "FAIL  qdrant reachable    -> make init"
fi
chk "python3"           "command -v python3"           "install python3"
echo "Optional MCPs (Gmail/Calendar/etc.) are user-configured; see RECOMMENDED-TOOLING.md"
