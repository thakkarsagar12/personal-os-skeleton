#!/bin/bash
# Personal OS — Infrastructure Startup & Health Check
# Called at the start of every Claude Code conversation
# Ensures Postgres + Qdrant are running and personal_os DB is accessible

PROJECT_DIR="${PERSONAL_OS_ROOT}"
MEMORY_PY="$PROJECT_DIR/system/db/memory.py"
PENDING_DIR="$PROJECT_DIR/system/db/pending"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

status_ok=true

# --- Check incognito mode ---
if [ -f "$PROJECT_DIR/system/.incognito" ]; then
    echo -e "${YELLOW}[INCOGNITO] Session recording disabled${NC}"
    exit 0
fi

# --- Check Docker ---
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}[FAIL] Docker is not running${NC}"
    echo "Action: Start Docker Desktop"
    echo -e "${YELLOW}[FALLBACK] Markdown-only mode — saves go to system/db/pending/${NC}"
    exit 1
fi

# --- Check Postgres ---
pg_status=$(docker inspect --format='{{.State.Health.Status}}' pos_postgres 2>/dev/null)
if [ "$pg_status" = "healthy" ]; then
    echo -e "${GREEN}[OK] Postgres (port 5432) — healthy${NC}"
else
    echo -e "${YELLOW}[STARTING] Postgres...${NC}"
    cd "$PROJECT_DIR" && docker compose up -d postgres
    # Wait for healthy status (max 30s)
    for i in $(seq 1 6); do
        sleep 5
        pg_status=$(docker inspect --format='{{.State.Health.Status}}' pos_postgres 2>/dev/null)
        if [ "$pg_status" = "healthy" ]; then
            break
        fi
    done
    if [ "$pg_status" = "healthy" ]; then
        echo -e "${GREEN}[OK] Postgres — started${NC}"
    else
        echo -e "${RED}[FAIL] Postgres — could not start${NC}"
        status_ok=false
    fi
fi

# --- Check Qdrant ---
qd_status=$(docker inspect --format='{{.State.Health.Status}}' pos_qdrant 2>/dev/null)
if [ "$qd_status" = "healthy" ]; then
    echo -e "${GREEN}[OK] Qdrant (port 6333) — healthy${NC}"
else
    echo -e "${YELLOW}[STARTING] Qdrant...${NC}"
    cd "$PROJECT_DIR" && docker compose up -d qdrant
    for i in $(seq 1 6); do
        sleep 5
        qd_status=$(docker inspect --format='{{.State.Health.Status}}' pos_qdrant 2>/dev/null)
        if [ "$qd_status" = "healthy" ]; then
            break
        fi
    done
    if [ "$qd_status" = "healthy" ]; then
        echo -e "${GREEN}[OK] Qdrant — started${NC}"
    else
        echo -e "${RED}[FAIL] Qdrant — could not start${NC}"
        status_ok=false
    fi
fi

# --- Check personal_os DB exists ---
if [ "$status_ok" = true ]; then
    db_check=$(docker exec pos_postgres psql -U postgres -d personal_os -c "SELECT 1" 2>&1)
    if echo "$db_check" | grep -q "1"; then
        echo -e "${GREEN}[OK] personal_os database — accessible${NC}"
    else
        echo -e "${RED}[FAIL] personal_os database — not accessible${NC}"
        status_ok=false
    fi

    # --- Check tables exist ---
    table_count=$(docker exec pos_postgres psql -U postgres -d personal_os -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'" 2>/dev/null | tr -d ' ')
    if [ "$table_count" -ge 7 ] 2>/dev/null; then
        echo -e "${GREEN}[OK] Schema — $table_count tables found${NC}"
    else
        echo -e "${RED}[FAIL] Schema — expected 7 tables, found $table_count${NC}"
        status_ok=false
    fi
fi

# --- Real host->container TCP check (catches port-binding/proxy failures
#     that docker-exec checks above cannot see, e.g. IDE proxy on the port) ---
if [ "$status_ok" = true ]; then
    if python3 -c "import socket,sys; socket.create_connection(('localhost',5432),3).close()" 2>/dev/null; then
        echo -e "${GREEN}[OK] Postgres reachable from host (localhost:5432)${NC}"
    else
        echo -e "${RED}[FAIL] Postgres NOT reachable on host localhost:5432 — container healthy but host port unbound (proxy/IDE conflict?). memory.py will fail.${NC}"
        status_ok=false
    fi
    if curl -sf -m 3 http://localhost:6333/healthz >/dev/null 2>&1; then
        echo -e "${GREEN}[OK] Qdrant reachable from host (localhost:6333)${NC}"
    else
        echo -e "${RED}[FAIL] Qdrant NOT reachable on host localhost:6333 — semantic layer will fail.${NC}"
        status_ok=false
    fi
fi

# --- Process pending markdown files if DB is ready ---
if [ "$status_ok" = true ]; then
    pending_count=$(find "$PENDING_DIR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$pending_count" -gt 0 ]; then
        echo -e "${YELLOW}[SYNC] $pending_count pending session(s) found — syncing to DB...${NC}"
        python3 "$MEMORY_PY" sync
        echo -e "${GREEN}[OK] Pending sessions synced${NC}"
    fi
fi

# --- Summary ---
echo ""
if [ "$status_ok" = true ]; then
    echo -e "${GREEN}Infrastructure ready. Conversation memory is live.${NC}"
else
    echo -e "${YELLOW}Some services failed. Operating in markdown-only mode.${NC}"
    echo -e "${YELLOW}Saves will go to system/db/pending/ and sync when DB is back.${NC}"
    exit 1
fi
