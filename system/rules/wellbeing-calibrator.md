---
name: wellbeing-calibrator
purpose: Self-rated energy and stress levels adapt the task load presented each session.
enabled: disabled by default
---

# Wellbeing Calibrator

## Purpose

Adapt the system's task recommendations to how the user is actually feeling right now.
A high-energy day and a low-energy day should not receive the same task list.

---

## Check-In Protocol

### When to check in

- During `/morning`: ask for today's energy level (1–5 scale).
- During `/evening`: ask for end-of-day energy and stress (1–5 each).
- If the user's messages signal frustration, low energy, or overwhelm, offer a brief check-in.

### Scale

| Rating | Meaning |
|--------|---------|
| 1 | Very low — depleted |
| 2 | Low — reduced capacity |
| 3 | Normal — baseline operations |
| 4 | Good — can push |
| 5 | High — ambitious sessions |

---

## Calibration Logic

| State | Behavior |
|-------|---------|
| Energy 1–2 | Reduce task load. Suggest lighter, lower-friction work. Do not push ambitious items. |
| Energy 3 | Normal operations. Standard task list. |
| Energy 4–5 | Push harder. Surface deep-work tasks and ambitious priorities. |
| Stress 4–5 for 3+ consecutive days | Flag it. Recommend dropping or deferring something. |

---

## Weekly Recalibration

During `/weekly-review`, reflect on the week's energy/stress pattern:
- Were there recurring low-energy periods? Identify the pattern.
- Were tasks consistently too heavy or too light?
- Adjust the default task volume for the coming week accordingly.

The system adapts to the user — a difficult week means a lighter plan, not guilt.

---

## Tracking

Store check-in data in `system/wellbeing.md` (create if absent). Format:

```
| Date | Energy (1-5) | Stress (1-5) | Notes |
|------|-------------|-------------|-------|
```

---

*Module: disabled by default. Enable during `/init-os` or via orchestrator instruction.*
