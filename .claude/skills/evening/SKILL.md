---
name: evening
description: "End-of-day review — surfaces done/undone tasks, prompts a brief energy/reflection note, and updates today's file. Use each evening to close the day, capture any loose threads, and prepare tomorrow's starting point."
---

# Evening Review (`/evening`)

## What This Skill Does

Produces a structured end-of-day summary covering:

1. **Done vs undone** — compares today's completed tasks against what was open at morning
2. **Wins** — highlights what moved forward today
3. **Open threads** — items left open, with a carry-forward suggestion
4. **Brief reflection** — one optional free-text note appended to today's review file
5. **Goal Compass check** — did today push the active pillar?

## Invocation

```
/evening
```

No arguments required.

---

## Execution Steps

### Step 1 — Date Check

```bash
date   # confirm today's date
```

### Step 2 — Task Delta

Read `daily-ops/tasks/today.md`.

Classify each task:
- `[x]` → Done
- `[ ]` → Open / carry-forward
- `[~]` → In-progress

Output counts: **Done: N | Open: N | In-progress: N**

### Step 3 — Wins

List completed items. Keep to bullet points — no elaboration unless the item is notable.

### Step 4 — Open Threads

For each open/in-progress task, suggest one of:
- **Carry to tomorrow** → add to `daily-ops/tasks/today.md` for next day (or prompt user)
- **Backlog** → move to `daily-ops/tasks/backlog.md` if not urgent

### Step 5 — Goal Compass Check

Read `system/goal-compass.md`. Answer:
> "Pillar **{PILLAR_NAME}**: moved / not moved today"

### Step 6 — Reflection Prompt

Offer a single optional prompt:
> "Anything to note about today? (press Enter to skip)"

If provided, append a datestamped note to `daily-ops/reviews/{YYYY-MM-DD}.md`.

### Step 7 — Output Format

```
## Evening — {YYYY-MM-DD}

**Done: N | Open: N | In-progress: N**

### Wins
- Task A ✓
- Task B ✓

### Open Threads
- Task C → carry to tomorrow
- Task D → backlog

### Compass
Pillar **{PILLAR_NAME}**: moved / not moved

### Note
{User's reflection note, if provided}
```

---

## Configuration

| Setting | Location | Notes |
|---------|----------|-------|
| Daily tasks | `daily-ops/tasks/today.md` | Source of truth for today |
| Backlog | `daily-ops/tasks/backlog.md` | Overflow tasks |
| Daily review | `daily-ops/reviews/{YYYY-MM-DD}.md` | Created if not present |
| Goal compass | `system/goal-compass.md` | North star + pillars |

---

## Output Rules

- Short by default — one screen maximum.
- No lecturing or moralising about what wasn't done.
- Validate progress first, then surface gaps briefly.
- One carry-forward action recommended, not a list.
