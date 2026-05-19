# Architecture

Personal OS is a pure-markdown knowledge base operated through Claude Code CLI. It has no
application server, no database schema to migrate, and no build step. All intelligence lives
in Claude Code agents and skills; all data lives in markdown files.

---

## Domains

The minimal-core skeleton ships with three operational domains:

| Domain | Key | Root Path | Domain Index | Purpose |
|--------|-----|-----------|-------------|---------|
| Daily Ops | `ops` | `daily-ops/` | `daily-ops/_index.md` | Tasks, habits, routines, reviews |
| Second Brain | `brain` | `second-brain/` | `second-brain/_index.md` | Capture, notes, ideas, knowledge |
| Study | `study` | `study/` | `study/_index.md` | Learning tracks, roadmaps, progress |

Each domain has a `_index.md` that is the **token-cheap entry point**: agents always read it
first rather than recursing into subdirectory files unless specifically needed.

Additional domains can be added at any time; see [EXTENDING.md](EXTENDING.md).

---

## Agent Hierarchy

Agents live in `.claude/agents/`. The system uses a strict three-tier pipeline:

```
master-orchestrator
    ├── daily-ops-lead
    │       ├── task-agent
    │       ├── routine-agent
    │       └── review-agent
    ├── second-brain-lead
    │       ├── capture-agent
    │       └── organizer-agent
    └── study-lead
            └── study-agent
```

**Counts:** 1 orchestrator + 3 domain leads + 6 specialist agents = 10 agents total.

### Tier 1 — master-orchestrator

`master-orchestrator` is the single entry point for every user request. It:

1. Interprets the request and identifies which 1–2 domain leads are relevant.
2. Spawns selected leads in parallel (using the `Task` tool).
3. Collects outputs and returns a unified response.

It runs on `opus` (highest-capability model) and has `Task` in its toolset.

### Tier 2 — Domain Leads

Each lead owns one domain. Leads receive a scoped sub-task from the orchestrator, coordinate
their specialist agents, and return a merged answer upward.

| Lead | Domain | Specialist Agents |
|------|--------|------------------|
| `daily-ops-lead` | Tasks, habits, routines, schedule, reviews | task-agent, routine-agent, review-agent |
| `second-brain-lead` | Capture, notes, ideas, research, bookmarks | capture-agent, organizer-agent |
| `study-lead` | Learning tracks, roadmaps, progress, revision | study-agent |

Leads run on `opus` and include the `Task` tool so they can spawn specialists.

### Tier 3 — Specialist Agents

Specialists focus on a single responsibility. They receive a scoped sub-task from their lead,
do the work (read/write files, query MCPs), and return output to the lead — **not directly to
the user**.

| Agent | Role | Parent Lead |
|-------|------|------------|
| `task-agent` | Task management — add, list, complete, next | daily-ops-lead |
| `routine-agent` | Daily routines and habits tracking | daily-ops-lead |
| `review-agent` | Daily/weekly reviews, elimination rule | daily-ops-lead |
| `capture-agent` | Quick capture to `second-brain/inbox/` | second-brain-lead |
| `organizer-agent` | Organize notes and knowledge | second-brain-lead |
| `study-agent` | Study sessions, notes, cards, revision | study-lead |

Specialists run on `sonnet` and typically do not need the `Task` tool.

---

## Slash Commands (Skills)

Skills live in `.claude/skills/`. Each skill directory contains a `SKILL.md` that defines
the execution steps for that slash command.

| Skill | Command | Purpose |
|-------|---------|---------|
| `morning` | `/morning` | Morning briefing — tasks, habits, date check |
| `evening` | `/evening` | Evening review — done/undone, energy check |
| `weekly-review` | `/weekly-review` | Weekly summary — wins, misses, patterns |
| `capture` | `/capture [text]` | Quick capture to `second-brain/inbox/` |
| `task` | `/task [...]` | Task management — add, list, done, next |
| `focus` | `/focus [key/combo]` | Activate a domain subset |
| `backlinks` | `/backlinks [entity]` | Show files referencing an entity via `[[wiki-link]]` |
| `lint` | `/lint [--fix] [path]` | KB audit — orphans, broken links, stale dates |

Additional built-in commands (defined in `CLAUDE.md`, not a `SKILL.md` file):

| Command | Purpose |
|---------|---------|
| `/init-os` | First-run personalisation — fills `{{...}}` placeholders, enables rule modules |
| `/reload` | Full system audit — reads all config, shows gaps, accepts updates |
| `/incognito [on/off/status]` | Toggle session privacy (disables memory capture) |

---

## Focus System

`/focus` activates a domain subset for the current session. Domain keys and pre-defined
combos are documented in `system/active-context.md`.

**Domain keys:** `ops`, `brain`, `study`

**Built-in combos:**

| Combo | Domains | Use Case |
|-------|---------|----------|
| `plan-week` | ops + study | Weekly planning — tasks and learning |
| `deep-work` | study + brain | Focused study session |
| `review` | ops + brain | Daily/weekly review |
| `full` | all | Everything loaded |

---

## Operating Rules

Rule bodies live in `system/rules/`. All modules are **disabled by default** and opt-in
via `/init-os` or by editing `system/rules.md`.

| Module | What It Does |
|--------|-------------|
| `elimination.md` | Caps weekly active priorities; overflow goes to backlog |
| `wellbeing-calibrator.md` | Energy/stress self-rating adapts task load |
| `spaced-repetition.md` | Spaced repetition schedule and revision modes |
| `date-awareness.md` | Verifies current date at session start |

See [CUSTOMIZING.md](CUSTOMIZING.md) for how to enable modules.

---

## Memory DB + Repo RAG

Two persistent stores backed by local Docker: Postgres (relational) + Qdrant (vectors).

Full architecture, CLI, and protocols: `system/memory-db.md`

### Memory DB

Stores conversation history in typed segments (discussion, decision, plan-change, insight,
action, blocker). Two layers:

- **Base** — conversations + segments in Postgres
- **Intelligence** — summaries, topics, decisions, pointers with vector search in Qdrant

**Embedding model:** `all-MiniLM-L6-v2` (384 dimensions), runs locally via
`sentence-transformers`.

### Repo RAG

`system/db/repo_index.py` indexes all repo markdown by H2 heading into the `personal_os_repo`
Qdrant collection. Enables semantic search over the KB itself.

```bash
python system/db/repo_index.py index     # full re-index
python system/db/repo_index.py search "your question"
```

### System DB Files

| File | Role |
|------|------|
| `system/db/startup.sh` | Health check at session start — verifies Postgres + Qdrant |
| `system/db/memory.py` | Conversation memory CLI |
| `system/db/repo_index.py` | Repo RAG CLI — index/search repo markdown |
| `system/db/bridge.py` | claude-mem → Postgres/Qdrant nightly bridge |
| `system/db/startup_check.py` | Python health check helper |

### claude-mem Bridge

`claude-mem` is the live write-ahead capture layer: every session is automatically recorded
to a local SQLite database. The bridge (`bridge.py`) runs nightly (and on session end via
Stop hook) to mirror those records into Postgres/Qdrant. **No manual session start is
required** — memory is captured automatically.

---

## Infrastructure

| Component | Role | Config |
|-----------|------|--------|
| Postgres | Relational conversation store | `$PGHOST:$PGPORT`, db `personal_os` |
| Qdrant | Vector embeddings (semantic search) | `$QDRANT_HOST:$QDRANT_HTTP_PORT` |
| `docker-compose.yml` | Brings up both containers | project root |

Ports are read from environment variables — no hardcoded values. Copy `.env.example` to `.env`
and set `PGPORT` and `QDRANT_HTTP_PORT` to values that do not conflict with other local services.

---

## Data Flow

```
User request
    │
    ▼
master-orchestrator          ← reads system/active-context.md for loaded domains
    │
    ├─(parallel)─────────────────────────────────────────────┐
    ▼                                                         ▼
domain-lead (e.g. daily-ops-lead)                   domain-lead (e.g. study-lead)
    │                                                         │
    ├── reads {domain}/_index.md   (token-cheap)             │
    ├── spawns specialist(s)                                  │
    └── collects output                                       └── same pattern
    │
    ▼
master-orchestrator collects all lead outputs → unified response to user
```

**File access pattern:** `_index.md` first (always) → specific files only when needed.

---

## Key Data Locations

| Data | Path |
|------|------|
| Today's tasks | `daily-ops/tasks/today.md` |
| Task backlog | `daily-ops/tasks/backlog.md` |
| Daily reviews | `daily-ops/reviews/` |
| Weekly reviews | `daily-ops/reviews/weekly/` |
| Inbox captures | `second-brain/inbox/` |
| Study notes | `study/{track}/notes/` |
| Study cards | `study/{track}/cards/{topic}.md` |
| Study roadmaps | `study/{track}/roadmap.md` |
| Study progress | `study/progress.md` |
| Goal compass | `system/goal-compass.md` |
| Active domains | `system/active-context.md` |
| Rule modules | `system/rules/` |
| System registry | `system/registry.md` |

---

## Canonical Reference

- `system/registry.md` — single source of truth for all agents, skills, rules, and paths
- `CLAUDE.md` — master instructions file read by Claude Code at session start
- `system/memory-db.md` — full memory DB architecture and CLI reference
