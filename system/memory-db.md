---
name: memory-db
purpose: Conversation memory DB + repo RAG — architecture, setup, and CLI reference.
---

# Conversation Memory DB + Repo RAG

Two persistent stores backed by local Docker: Postgres (relational) + Qdrant (vectors).

---

## Architecture

```
Conversation Memory (dialogue history):
  Layer 2 (Intelligence):  summaries + topics + decisions + pointers   [semantic search via Qdrant]
                           ─────────────────────────────────────────
  Layer 1 (Base):          conversations + segments                    [typed chunks in Postgres]

Repo RAG (file retrieval):
  personal_os_repo         repo markdown chunks by H2 heading + frontmatter  [semantic search via Qdrant]
```

Segments are 3–5 sentence typed chunks. Supported types: `discussion`, `decision`,
`plan-change`, `insight`, `action`, `blocker`. Relational data in Postgres; vector
embeddings in Qdrant. No raw message storage.

---

## Infrastructure

| Component | Role | Config |
|-----------|------|--------|
| Postgres | Relational store for conversations + segments | `$PGHOST:$PGPORT`, db `personal_os` |
| Qdrant | Vector search for summaries, pointers, repo chunks | `$QDRANT_HOST:$QDRANT_HTTP_PORT` |
| docker-compose.yml | Brings up both containers | project root |

Port values come from environment variables. Copy `.env.example` to `.env` and set:

```
PGPORT=<your-postgres-port>
QDRANT_HTTP_PORT=<your-qdrant-http-port>
```

The `system/db/` scripts read these automatically.

### Qdrant Collections

| Collection | Contents |
|-----------|---------|
| `personal_os_segments` | Conversation segments |
| `personal_os_summaries` | Conversation summaries |
| `personal_os_pointers` | Insights, decisions, action items |
| `personal_os_repo` | Repo markdown chunks (RAG) |

### Embedding Model

`all-MiniLM-L6-v2` (384 dimensions) — runs locally via `sentence-transformers`.

---

## System DB Files (`system/db/`)

| File | Role |
|------|------|
| `startup.sh` | Health check at session start — verifies Postgres + Qdrant are reachable |
| `memory.py` | Conversation memory CLI — start/segment/end/search sessions |
| `repo_index.py` | Repo RAG CLI — index repo markdown, semantic search |
| `bridge.py` | claude-mem → Postgres/Qdrant bridge (nightly cron + session Stop hook) |
| `startup_check.py` | Python health check helper used by startup.sh |

---

## claude-mem Bridge

`claude-mem` is the live write-ahead capture layer: every session is automatically
recorded to a local SQLite database by the claude-mem observer. The bridge (`bridge.py`)
runs nightly and after each session ends to mirror those records into Postgres/Qdrant.

This means **no manual session start is required** — memory is captured automatically.
Use `memory.py` only for explicit mid-session checkpoints.

```bash
python system/db/bridge.py status    # show watermark + record counts
python system/db/bridge.py sync      # incremental sync (since watermark)
python system/db/bridge.py sync --backfill   # sync from epoch 0 (first run / gap fill)
```

Configure which project labels to sync by editing `PROJECTS` in `bridge.py`.

---

## Session Start Protocol

At the start of every conversation:

1. Run `bash system/db/startup.sh` — health check (Postgres + Qdrant). Warn and continue if failing.
2. Read `system/wellbeing.md` if the wellbeing-calibrator rule is enabled.

---

## CLI — Conversation Memory

```bash
# Install Python deps (one time)
pip install -r system/db/requirements.txt

# Docker (one time / on machine restart)
docker compose up -d

# Smart commands (auto-fallback to markdown if DB is down)
python system/db/memory.py smart-start "Session title" --domains study
python system/db/memory.py smart-segment <session_id> "content" --type discussion
python system/db/memory.py smart-end <session_id> --summary "..." --outcomes "..."

# Search
python system/db/memory.py search "query"
python system/db/memory.py timeline "topic-name"
python system/db/memory.py decisions --topic "topic-name"
python system/db/memory.py pointers --topic "topic-name"
python system/db/memory.py recent --limit 10

# Sync pending markdown files to DB
python system/db/memory.py sync

# Check DB availability
python system/db/memory.py check-db
```

---

## CLI — Repo RAG

```bash
# Full (re)index — chunks all repo markdown by H2 heading
python system/db/repo_index.py index

# Incremental — only files modified in last N hours
python system/db/repo_index.py index --changed-since 24

# Semantic search
python system/db/repo_index.py search "your question in natural language"
python system/db/repo_index.py search "query" --domain system --top 3

# Stats
python system/db/repo_index.py status
python system/db/repo_index.py list-domains
```

**When to use:** exploratory questions, "where did we write about X", broad context retrieval.
**When NOT to use:** you already know the file path — use Read directly (cheaper).

---

## Markdown Fallback

If the database is unavailable, `smart-*` commands save sessions to `system/db/pending/*.md`.
When the database comes back online, `startup.sh` auto-syncs the pending files. No data is lost.

---

## Incognito Mode

`/incognito on` disables all saving for the session.
`/incognito off` re-enables.
`/incognito status` shows current state.

---

## Real-Time Logging

Log segments as events happen, not only at session end:

| Event | DB Action |
|-------|-----------|
| Topic discussed | `segment` (discussion) + `pointer` (insight) |
| Decision made | `segment` (decision) |
| Plan changed | `segment` (plan-change) |
| New insight | `pointer` (insight) |
| Action item | `pointer` (action) |
| Blocker identified | `segment` (blocker) |

---

## Keeping RAG Fresh

Re-index after major changes:

```bash
python system/db/repo_index.py index --changed-since 24
```

---

## PII Scanner

Before committing or sharing, verify no personal data has leaked into repo files:

```bash
bash scripts/scan-core.sh .   # expect: scan-core: CLEAN
```

Populate `scripts/identifiers.txt` with your real names, email, phone numbers, and any
other personal identifiers so the scanner catches leaks specific to your setup.

---

*Generic architecture doc. Ports and paths are read from environment variables and .env — no hardcoded values.*
