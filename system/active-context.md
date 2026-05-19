---
name: active-context
purpose: Tracks which domains are currently loaded. Updated by /focus command.
---

# Active Context

Tracks which domains are active for the current session. Updated by `/focus`.

## Active Domains (default)

- **Daily Ops** (`ops`) — task management, habits, routines, reviews
- **Second Brain** (`brain`) — capture, notes, ideas, knowledge
- **Study** (`study`) — learning tracks, progress, revision

All three domains are active by default in the minimal skeleton. Use `/focus` to activate
a subset or to add additional domains if you have extended the system.

---

## Available Domains

| Domain | Key | Agents Activated |
|--------|-----|-----------------|
| Daily Ops | `ops` | daily-ops-lead → routine-agent, task-agent, review-agent |
| Second Brain | `brain` | second-brain-lead → capture-agent, organizer-agent |
| Study | `study` | study-lead → study-agent |

---

## Focus Command

```
/focus ops          # daily ops only
/focus brain        # second brain only
/focus study        # study only
/focus ops brain    # two domains simultaneously
/focus all          # all three domains
```

---

*Updated: on `/focus` command. Default state = all 3 domains active.*
