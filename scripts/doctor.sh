#!/usr/bin/env bash
set -u
chk(){ if eval "$2" >/dev/null 2>&1; then echo "PASS  $1"; else echo "FAIL  $1  -> $3"; fi; }
[ -f .env ] && . ./.env
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
DOCKER_UP=0; docker info >/dev/null 2>&1 && DOCKER_UP=1
chk "docker installed"  "command -v docker"            "install Docker"
chk "docker running"    "[ $DOCKER_UP = 1 ]"           "start Docker Desktop"

# Real port check: PASS if nothing is listening on POSTGRES_PORT, OR if our
# own compose postgres is the listener (so it doesn't false-FAIL post make init).
chk "postgres port free or ours" \
  "! lsof -nP -iTCP:${POSTGRES_PORT} -sTCP:LISTEN >/dev/null 2>&1 || docker compose ps postgres 2>/dev/null | grep -q Up" \
  "port ${POSTGRES_PORT} occupied by another process — run: lsof -nP -iTCP:${POSTGRES_PORT}"

# Only probe compose service state when docker daemon is actually up;
# avoids hangs from 'docker compose ps' talking to an unreachable daemon.
if [ $DOCKER_UP = 1 ]; then
  chk "compose file"      "test -f docker-compose.yml"   "run from repo root"
  chk "postgres reachable" "docker compose ps postgres | grep -q Up" "make init"
  chk "qdrant reachable"   "docker compose ps qdrant   | grep -q Up" "make init"
else
  echo "FAIL  compose file (skipped — docker not running)"
  echo "FAIL  postgres reachable  -> make init"
  echo "FAIL  qdrant reachable    -> make init"
fi
chk "python3"           "command -v python3"           "install python3"
echo "Optional MCPs (Gmail/Calendar/etc.) are user-configured; see RECOMMENDED-TOOLING.md"
