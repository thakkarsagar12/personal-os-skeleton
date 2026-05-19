---
name: "Morning Briefing"
description: "Daily morning briefing — surfaces today's tasks, calendar events, and habits checklist. Optionally integrates with Gmail and Google Calendar MCPs when configured. Use at the start of each day to orient, prioritise, and commit to the day's work."
---

# Morning Briefing (`/morning`)

## What This Skill Does

Produces a structured start-of-day summary covering:

1. **Today's tasks** — reads `daily-ops/tasks/today.md`, surfaces open items
2. **Calendar** (optional MCP) — lists today's events if Google Calendar MCP is configured
3. **Inbox** (optional MCP) — flags any urgent items if Gmail MCP is configured
4. **Habits checklist** — reads the active habits list and renders a checklist for today
5. **Goal Compass pulse** — one-line reminder of today's priority pillar (from `system/goal-compass.md`)

## Invocation

```
/morning
```

No arguments required. Runs silently when optional MCPs return nothing urgent.

---

## Execution Steps

### Step 1 — Date & Infra

```bash
date                          # confirm today's date
bash system/db/startup.sh     # health-check Postgres / Qdrant (if memory layer is enabled)
```

Read `system/behavior-log.md` — calibrate to confirmed patterns.

### Step 2 — Tasks

Read `daily-ops/tasks/today.md`. Summarise:
- Open tasks (count + top 3 by priority)
- Any overdue items carried from yesterday

### Step 3 — Calendar (optional)

If Google Calendar MCP is configured, call `list_events` for today.
- Render as a compact timeline.
- If MCP is not configured, skip silently.

### Step 4 — Email (optional)

If Gmail MCP is configured, call `search_threads` for unread/starred messages from the past 24 h.
- Surface only items that require action today.
- If MCP is not configured, skip silently.

### Step 5 — Habits

Read the habits list (location configured by user — default: `daily-ops/habits/habits.md`).
Render as a markdown checklist for today.

### Step 6 — Goal Compass Pulse

Read `system/goal-compass.md`. Output a single line:
> "Today's pillar: **{PILLAR_NAME}** — {one-line reminder}"

### Step 7 — Output Format

```
## Morning — {YYYY-MM-DD}

### Tasks (N open)
- [ ] Task A  [priority]
- [ ] Task B  [priority]
...

### Calendar
HH:MM – HH:MM  Event title
...

### Habits
- [ ] Habit 1
- [ ] Habit 2
...

### Compass
Today's pillar: **{PILLAR_NAME}** — {reminder}
```

Keep the output under one screen. If calendar/email MCPs are absent, omit those sections without comment.

---

## Configuration

| Setting | Location | Notes |
|---------|----------|-------|
| Habits list | `daily-ops/habits/habits.md` | One habit per line |
| Goal compass | `system/goal-compass.md` | North star + pillars |
| Active tasks | `daily-ops/tasks/today.md` | Daily task file |
| Calendar MCP | User's MCP config | Optional |
| Gmail MCP | User's MCP config | Optional |

---

## Output Rules

- **Short by default.** Lead with tasks. 2 lines > 10.
- Bullets and headers, no walls of text.
- Silent when MCPs return nothing — no "no events found" noise.
- One next action recommended at the end if tasks are ambiguous.
