---
domain: study
---

# Study — Index

Learning tracks, roadmaps, notes, progress. One folder per track you define.

**Always read this file first** before diving into track subdirectories — it is the token-cheap summary of what is live in this domain.

---

## Structure

Each learning track lives at `study/{track}/` and follows this layout:

| Path | Class | Purpose |
|------|-------|---------|
| `{track}/roadmap.md` | WIKI | Track roadmap — milestones with `[ ]` / `[~]` / `[x]` status |
| `{track}/notes/` | WIKI | Topic-level notes (one file per topic) |
| `{track}/cards/` | STATE | Q&A cards auto-generated per study session |
| `progress.md` | LOG | Weekly progress log across all tracks |

Use `study/roadmap.template.md` to bootstrap a new track's roadmap.

---

## Tracks

_One folder per track you define. Add rows here as you create tracks._

| Track | Path | Status |
|-------|------|--------|
| _(add your tracks here)_ | `study/{track}/` | — |

---

## Agents

| Agent | Role |
|-------|------|
| `study-lead` | Domain lead — coordinates study sessions and progress |
| `study-agent` | Study sessions, note capture, card generation, spaced repetition |

---

## Pipeline Flow (Study → Second Brain)

Completed topics auto-publish to the Second Brain — no manual copy:

```
study/{track}/notes/{topic}.md    (learning context)
        ↓  [topic marked [x] done]
second-brain/notes/study/{track}/{topic}.md    (polished, cross-referenced)
```

---

## Freshness Rules

- `progress.md` weekly log should have entries within the last 7 days.
- Cards are created per session — gaps drive revision priority.
- Revision due dates tracked in `system/spaced-repetition.md` (if that rule module is enabled).
