---
name: elimination-rule
purpose: Cap weekly active priorities and overflow excess to a backlog.
enabled: disabled by default
---

# Elimination Rule

## Purpose

Prevent overload by enforcing a hard cap on active weekly priorities. Anything beyond the
cap moves to `tasks/backlog.md` rather than staying in the active list and silently slipping.

---

## The Rule

### Weekly Cap

At the start of each week (or during `/weekly-review`):

1. List all tasks carried forward from the previous week.
2. For each carried item ask: "Is this still relevant? Drop it or commit to it this week."
3. Apply the hard cap: **maximum N active priorities per week** (set N during `/init-os`, default 3).
4. All items beyond the cap move to `tasks/backlog.md`.
5. If more than 5 incomplete tasks have been carried forward for 2+ weeks, surface a flag:
   "You are overloaded. What are we dropping?"

### Load Ratio Check

After listing weekly items, calculate: `(completed items) / (items added)`.
- Ratio > 1.0 means more is being added than completed — the system is overloading.
- Surface the ratio in `/weekly-review` output.

### Backlog Hygiene

- Backlog items are reviewed weekly during `/weekly-review`.
- Pull an item from backlog into the active week only if it is still relevant.
- Drop items that have been in backlog for 30+ days without being picked up.

---

## Configuration

Adjust the cap `N` by editing this file or instructing the orchestrator:

```
weekly_priority_cap: 3        # default; change to match your capacity
backlog_path: tasks/backlog.md
stale_threshold_days: 30
overload_carry_threshold: 5
overload_carry_weeks: 2
```

---

*Module: disabled by default. Enable during `/init-os` or via orchestrator instruction.*
