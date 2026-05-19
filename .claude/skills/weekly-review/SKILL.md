---
name: weekly-review
description: "End-of-week review — surfaces wins, misses, patterns, and enforces the priority cap (max 3 priorities, overflow to backlog). Produces a dated summary file. Use every week to close the cycle, recalibrate focus, and set next-week intentions."
---

# Weekly Review (`/weekly-review`)

## What This Skill Does

Produces a structured weekly retrospective covering:

1. **Task summary** — completed vs missed for the week
2. **Wins** — what moved forward
3. **Misses** — what didn't, with brief root-cause note
4. **Patterns** — recurring blockers or energy patterns observed
5. **Priority cap** — enforce max 3 active priorities; move overflow to backlog
6. **Next-week intentions** — 1-3 commitments for the coming week

## Invocation

```
/weekly-review
```

No arguments. Detects the current week automatically from `date`.

---

## Execution Steps

### Step 1 — Date & Range

```bash
date   # confirm today; derive week range (Mon–Sun)
```

### Step 2 — Task Harvest

Scan `daily-ops/reviews/` for daily files from this week (`{YYYY-MM-DD}.md`).
Also read `daily-ops/tasks/today.md` and `daily-ops/tasks/backlog.md`.

Build a flat list of all tasks worked on this week with status.

### Step 3 — Wins

List items marked `[x]` (done) across the week. Group by domain if more than 5.

### Step 4 — Misses

List items that were planned but remain `[ ]` or `[~]` across multiple days.
For each miss, note one likely reason (no analysis required — just the obvious one).

### Step 5 — Patterns

Look for recurring themes across the week's daily notes:
- Same task blocked multiple days?
- Certain time slots consistently unproductive?
- Any domain consistently neglected?

Output 1-3 pattern observations. Skip if nothing notable.

### Step 6 — Priority Cap (Elimination Rule)

Read `system/rules/active/elimination.md` if present (else apply default: max 3).

List current active priorities. If more than the cap:
- Keep the top N (user confirms or agent recommends based on goal compass)
- Move the rest to `daily-ops/tasks/backlog.md` with a `[parked YYYY-MM-DD]` prefix

State clearly: **"Active priorities: N / Cap: 3"**

### Step 7 — Next-Week Intentions

Propose 1-3 specific commitments for next week, derived from:
- Carried-over high-priority tasks
- Goal compass pillar(s) that didn't move this week
- Any pattern that should be addressed

### Step 8 — Write Summary

Write the review to `daily-ops/reviews/weekly/{YYYY-WNN}.md` (ISO week number).

### Step 9 — Output Format

```
## Weekly Review — {Mon YYYY-MM-DD} to {Sun YYYY-MM-DD}

**Done: N | Missed: N | Carried: N**

### Wins
- Item A
- Item B

### Misses
- Item C — {one-line reason}

### Patterns
- {Pattern observation}

### Priorities
Active: N / Cap: 3
Parked → backlog: Item X, Item Y

### Next Week
1. {Commitment}
2. {Commitment}
3. {Commitment}
```

---

## Configuration

| Setting | Location | Notes |
|---------|----------|-------|
| Daily reviews | `daily-ops/reviews/` | Source for week harvest |
| Weekly reviews | `daily-ops/reviews/weekly/` | Output location |
| Backlog | `daily-ops/tasks/backlog.md` | Overflow from priority cap |
| Elimination rule | `system/rules/active/elimination.md` | Optional; default cap = 3 |
| Goal compass | `system/goal-compass.md` | Guides next-week intentions |

---

## Output Rules

- One screen maximum for the interactive summary.
- Full detail written to file; summary shown inline.
- No moralising about misses — state and move on.
- Recommend one priority carry-over, not a laundry list.
