# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## What This Is

`{{PROJECT_NAME}}` — a personal OS / second brain operated through Claude Code CLI. Pure markdown knowledge base with agent-driven automation.

**Owner:** `{{USER_NAME}}` — `{{USER_ROLE}}`

## Architecture

The system has 3 operational domains:

| Domain | Path | Index | Purpose |
|--------|------|-------|---------|
| Daily Ops | `daily-ops/` | `daily-ops/_index.md` | Tasks, habits, routines, reviews, health |
| Second Brain | `second-brain/` | `second-brain/_index.md` | Capture, notes, ideas, reading, learnings |
| Study | `study/` | `study/_index.md` | Learning tracks, roadmaps, notes, progress |

**Always consult the domain `_index.md` FIRST.** It is the token-cheap summary of what is live in that domain. Read full files only for the specific state you need.

**Data flow:** User request → master-orchestrator → domain lead(s) → specialist agents → response.

## Agent Architecture

### Master Pipeline

- **`master-orchestrator`** — Routes to domain leads based on request type. Entry point for all questions.

### Domain Leads

| Lead | Domain | Specialist Agents |
|------|--------|-------------------|
| `daily-ops-lead` | Tasks, habits, routines, schedule | task, routine, review |
| `second-brain-lead` | Capture, notes, ideas, research | capture, organizer |
| `study-lead` | Learning tracks, progress tracking | study |

**How it works:** master-orchestrator → 1-2 domain leads (parallel) → specialist agents → response.

## Focus System

`/focus [domain-key or combo]` activates specific domains. Multiple can run simultaneously.

**Domain keys:** `ops`, `brain`, `study`

**Combos:**

| Combo | Domains | Use Case |
|-------|---------|----------|
| `plan-week` | ops + study | Weekly planning — tasks and learning |
| `deep-work` | study + brain | Focused study session |
| `review` | ops + brain | Daily/weekly review |
| `full` | all | Everything loaded |

Config: `system/active-context.md`

## Goal Compass — North Star

**North Star:** `{{NORTH_STAR}}`

**Pillars:** `{{PILLAR_1}}` · `{{PILLAR_2}}` · `{{PILLAR_3}}` · `{{PILLAR_4}}` · `{{PILLAR_5}}`

Morning: "Which pillar am I pushing today?" Evening: "Did I move the needle?"

Config: `system/goal-compass.md`

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/morning` | Morning briefing — tasks, calendar, habits |
| `/evening` | Evening review — done/undone, energy check |
| `/weekly-review` | Weekly summary — wins, misses, patterns |
| `/capture [text]` | Quick capture to `second-brain/inbox/` |
| `/task [...]` | Task management — add, list, done, next, blocked |
| `/focus [domains/combo]` | Activate domains |
| `/reload` | Full system audit — gaps, updates, registry sync |
| `/lint` | Knowledge base audit — orphans, broken links, stale dates |
| `/backlinks [entity]` | Show files referencing an entity |
| `/init-os` | First-run personalisation — fills `{{...}}` placeholders, enables rule modules |
| `/incognito [on/off/status]` | Toggle session privacy |

### `/reload` Protocol

When `/reload` is invoked: read all system files → audit for gaps → present summary → accept updates. See `system/registry.md` for the canonical inventory.

## Operating Rules

Rule bodies live in `system/rules/`. The table below lists available modules; all are **disabled by default** and opt-in via `/init-os`.

| Module file | Name | What it does (summary) |
|-------------|------|------------------------|
| `elimination.md` | Elimination Rule | Enforces max-priority cap; overflow → backlog |
| `wellbeing-calibrator.md` | Wellbeing Calibrator | Adapts task load to energy/stress level |
| `spaced-repetition.md` | Spaced Repetition | Standard interval revision schedule for study topics |
| `date-awareness.md` | Date & Time Awareness | Checks current date each session; never carries stale dates |

To activate a module: set it to `enabled` in the `system/rules.md` table (or via `/init-os`).

## Communication Rules

- **One question at a time.** Never ask multiple questions in a single message.
- Applies to ALL agents.

## Conversation Memory + Repo RAG

Two Qdrant-backed stores on local Docker:

- **Conversation memory** — segments, summaries, topics, decisions, pointers (`system/db/memory.py`)
- **Repo RAG** — markdown chunks by H2 heading for token-cheap retrieval (`system/db/repo_index.py`)

Full architecture, CLI, and protocols: `system/memory-db.md`

**Start Protocol (each conversation):**
1. `bash system/db/startup.sh` — health-check infra (Postgres / Qdrant)
2. Read `system/behavior-log.md` if present — calibrate to confirmed patterns

**Retrieval before file-reading:**
- For exploratory questions, call `python system/db/repo_index.py search "query"` first — returns top-5 matching sections. Read ONLY those.
- For known paths, use Read directly.

**Privacy scanner:** `bash scripts/scan-core.sh <path>` — exit 0 + `scan-core: CLEAN` means no PII/denylisted content. Run before any commit or share. See `scripts/identifiers.txt` to configure your own identifiers.

## Key Conventions

- **Date format:** YYYY-MM-DD
- **Filenames:** kebab-case
- **Domain indexes:** always read `{domain}/_index.md` before diving into full files
- **Quick captures:** `second-brain/inbox/`
- **Tasks (daily):** `daily-ops/tasks/today.md`
- **Tasks (projects):** `daily-ops/tasks/projects/<project-name>.md`
- **Reviews:** `daily-ops/reviews/` (daily), `daily-ops/reviews/weekly/` (weekly)
- **Study notes:** `study/{track}/notes/`
- **Study roadmaps:** `study/{track}/roadmap.md`
