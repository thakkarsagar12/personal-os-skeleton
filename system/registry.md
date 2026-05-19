---
name: registry
purpose: Single source of truth for everything in the skeleton Personal OS. Used by /reload.
---

# System Registry

Single source of truth for the skeleton Personal OS. Used by `/reload` to audit,
display, and verify the system is consistent.

---

## Config Files

| File | Purpose | Critical |
|------|---------|----------|
| `CLAUDE.md` | Master instructions — domains, agents, commands, rules summary | yes |
| `system/rules.md` | Rule framework overview + module index | yes |
| `system/rules/elimination.md` | Opt-in: weekly priority cap + backlog overflow | no |
| `system/rules/wellbeing-calibrator.md` | Opt-in: energy/stress-adaptive task load | no |
| `system/rules/spaced-repetition.md` | Opt-in: SR schedule, queue, revision modes | no |
| `system/rules/date-awareness.md` | Opt-in: current-date check at session start | no |
| `system/goal-compass.md` | North star + 5-pillar template (fill via /init-os) | yes |
| `system/active-context.md` | Current focus mode / loaded domains | yes |
| `system/registry.md` | This file — system inventory | yes |
| `system/memory-db.md` | Conversation memory + repo RAG architecture | yes |
| `system/db/startup.sh` | Infra health check — Postgres + Qdrant | yes |
| `system/db/memory.py` | Conversation memory CLI | yes |
| `system/db/repo_index.py` | Repo RAG CLI — index/search repo markdown via Qdrant | yes |
| `system/db/bridge.py` | claude-mem → Postgres/Qdrant nightly bridge | yes |
| `system/db/startup_check.py` | Python startup health check helper | yes |

---

## Agent Definitions

Agents live in `.claude/agents/`.

| Agent File | Role | Parent |
|------------|------|--------|
| `master-orchestrator.md` | Routes requests to domain leads | root |
| `daily-ops-lead.md` | Tasks, habits, routines, schedule | master-orchestrator |
| `task-agent.md` | Task management | daily-ops-lead |
| `review-agent.md` | Daily/weekly reviews, elimination rule | daily-ops-lead |
| `routine-agent.md` | Daily routines and habits | daily-ops-lead |
| `second-brain-lead.md` | Capture, notes, ideas, research | master-orchestrator |
| `capture-agent.md` | Quick capture to inbox | second-brain-lead |
| `organizer-agent.md` | Organize notes and knowledge | second-brain-lead |
| `study-lead.md` | Learning tracks, progress | master-orchestrator |
| `study-agent.md` | Study sessions, notes, cards | study-lead |

**Counts:** 1 orchestrator + 3 leads + 6 specialists = 10 agents total.

---

## Skill Definitions

Skills live in `.claude/skills/`.

| Skill | Purpose |
|-------|---------|
| `morning/` | Morning briefing — tasks, habits, date check |
| `evening/` | Evening review — done/undone, energy check |
| `weekly-review/` | Weekly summary — wins, misses, patterns |
| `capture/` | Quick capture to `second-brain/inbox/` |
| `task/` | Task management — add, list, done, next |
| `focus/` | Activate domain subsets |
| `backlinks/` | Show files referencing an entity |
| `lint/` | Knowledge base audit — orphans, broken links, stale dates |
| `init-os/` | Conversational personalizer — fills in your name, domains, goal |

**Count:** 9 skills.

---

## Rule Modules

| Module | Status |
|--------|--------|
| `system/rules/elimination.md` | disabled by default |
| `system/rules/wellbeing-calibrator.md` | disabled by default |
| `system/rules/spaced-repetition.md` | disabled by default |
| `system/rules/date-awareness.md` | disabled by default |

---

## Domains

| Domain | Key | Root Path |
|--------|-----|-----------|
| Daily Ops | `ops` | `daily-ops/` |
| Second Brain | `brain` | `second-brain/` |
| Study | `study` | `study/` |

---

## Key Data Locations

| Data | Path |
|------|------|
| Today's tasks | `daily-ops/tasks/today.md` |
| Task backlog | `daily-ops/tasks/backlog.md` |
| Daily reviews | `daily-ops/reviews/` |
| Weekly reviews | `daily-ops/reviews/weekly/` |
| Inbox captures | `second-brain/inbox/` |
| Notes | `second-brain/notes/` |
| Study notes | `study/{track}/notes/` |
| Study cards | `study/{track}/cards/{topic}.md` |
| Study roadmaps | `study/{track}/roadmap.md` |
| Study progress | `study/progress.md` |
| Spaced rep queue | `system/spaced-repetition.md` (created on first use) |
| Wellbeing log | `system/wellbeing.md` (created on first use) |

---

## Slash Commands

| Command | Defined In |
|---------|-----------|
| `/morning` | `.claude/skills/morning/` |
| `/evening` | `.claude/skills/evening/` |
| `/weekly-review` | `.claude/skills/weekly-review/` |
| `/capture` | `.claude/skills/capture/` |
| `/task` | `.claude/skills/task/` |
| `/focus` | `.claude/skills/focus/` |
| `/backlinks` | `.claude/skills/backlinks/` |
| `/lint` | `.claude/skills/lint/` |

---

## Infrastructure

| Component | Role | Config |
|-----------|------|--------|
| Postgres | Relational conversation store | `$PGHOST:$PGPORT`, db `personal_os` |
| Qdrant | Vector embeddings (semantic search) | `$QDRANT_HOST:$QDRANT_HTTP_PORT` |
| docker-compose.yml | Brings up both containers | project root |
| claude-mem | Live write-ahead capture layer | `$CLAUDE_MEM_DB` (see claude-mem docs) |
| bridge.py | Nightly sync: claude-mem → Postgres/Qdrant | cron + session Stop hook |

---

## PII Scanner

```bash
bash scripts/scan-core.sh .   # expect: scan-core: CLEAN
```

Identifiers file: `scripts/identifiers.txt` (copy from `scripts/identifiers.example.txt`,
populate with your own real names/emails/phones before sharing the skeleton).

---

*Skeleton registry — reflects minimal core (3 domains, 10 agents, 9 skills, 4 rule modules).*
