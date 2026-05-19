---
domain: daily-ops
---

# Daily Ops — Index

Tasks, habits, routines, reviews. Day-to-day operational state.

**Always read this file first** before diving into subdirectory files — it is the token-cheap summary of what is live in this domain.

---

## Subdirectories

| Path | Purpose |
|------|---------|
| `tasks/` | Task files — today's priorities, project chains, backlog |
| `tasks/today.md` | Today's active task list (date-stamped; `/morning` rolls it daily) |
| `tasks/projects/` | Dependency-chain project task files (`<project-name>.md`) |
| `tasks/backlog.md` | Overflow tasks — items outside current max-priority cap |
| `reviews/` | Daily evening reviews (`YYYY-MM-DD.md`) |
| `reviews/weekly/` | Weekly reviews (`YYYY-Wxx.md`) |
| `routines/` | Morning/evening routine templates and protocols |
| `habits/` | Habit tracker grids and checklists |

---

## Active State (read these for "what is happening today")

| File | Class | Purpose |
|------|-------|---------|
| `tasks/today.md` | STATE | Today's priorities. Date header must match current date. |
| `habits/habit-tracker.md` | STATE | Current week's habit grid + daily checklist |

---

## Agents

| Agent | Role |
|-------|------|
| `daily-ops-lead` | Domain lead — coordinates all daily-ops specialists |
| `task-agent` | Task management — add, list, done, next, blocked |
| `routine-agent` | Daily routine and habit tracking |
| `review-agent` | Daily/weekly reviews, elimination rule enforcement |

---

## Skills

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `/morning` | `/morning` | Morning briefing — tasks, calendar, habits |
| `/evening` | `/evening` | Evening review — done/undone, energy check |
| `/weekly-review` | `/weekly-review` | Weekly summary — wins, misses, patterns |
| `/task` | `/task [...]` | Task management — add, list, done, next, blocked |

---

## Freshness Rules

- `tasks/today.md` header date must equal current date — else `/morning` flags and rolls it.
- Daily review missing for yesterday → `/morning` auto-generates stub.
- Weekly review triggers elimination rule (max-priority cap; overflow → `tasks/backlog.md`).

---

## Linked Systems

- Wellbeing data → `system/wellbeing.md` (if wellbeing-calibrator rule module enabled)
- Pillar alignment → `system/goal-compass.md`
- Behavior patterns → `system/behavior-log.md` (read at session start)
