---
domain: second-brain
---

# Second Brain — Index

Capture, notes, ideas, reading, learnings. Personal knowledge base.

**Always read this file first** before diving into subdirectory files — it is the token-cheap summary of what is live in this domain.

---

## Subdirectories

| Path | Purpose |
|------|---------|
| `inbox/` | Quick captures awaiting processing. Target: process within ~7 days. |
| `notes/` | Organized knowledge — notes by topic or category |
| `notes/study/` | Polished study notes auto-published from the Study domain (see Pipeline below) |

---

## Active State

| File | Class | Purpose |
|------|-------|---------|
| `inbox/` | LOG | Raw captures from `/capture`; organizer-agent processes and routes |

---

## Agents

| Agent | Role |
|-------|------|
| `second-brain-lead` | Domain lead — coordinates capture and organization |
| `capture-agent` | Quick capture to `inbox/`; no friction, no classification |
| `organizer-agent` | Process inbox items — classify, link, and move to `notes/` |

---

## Skills

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `/capture` | `/capture [text]` | Quick capture to `second-brain/inbox/` |
| `/backlinks` | `/backlinks [entity]` | Show all files that reference a given entity |
| `/lint` | `/lint` | Knowledge base audit — orphans, broken links, stale items |

---

## Pipeline Flow (Study → Second Brain)

When a study topic is marked complete (`[x]`), the study-agent auto-publishes a polished note:

```
study/{track}/notes/{topic}.md    (learning context)
        ↓  [topic marked [x] done]
second-brain/notes/study/{track}/{topic}.md    (polished, cross-referenced)
```

No manual copy needed. The organizer-agent can also pull inbox captures into the appropriate `notes/` subfolder.

---

## Freshness Rules

- `inbox/` items should be processed within ~7 days (organizer-agent).
- `notes/study/` updates automatically when study topics complete — no manual copy.
