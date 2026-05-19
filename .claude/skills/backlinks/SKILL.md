---
name: backlinks
description: "Finds all files in the knowledge base that reference a given entity via [[wiki-link]] syntax. Use to explore what the KB knows about a topic, person, project, or concept and how it is connected."
---

# Backlinks (`/backlinks`)

## What This Skill Does

Scans the markdown knowledge base for `[[wiki-link]]` references to a named entity and returns the file list with context snippets.

The `[[WikiLink]]` convention is the KB's internal linking standard — any `[[EntityName]]` in a markdown file creates a directed reference from that file to the entity. This skill inverts the graph: given an entity, find all files that point to it.

## Invocation

```
/backlinks <entity-name>
```

**Examples:**

```
/backlinks ProjectAlpha
/backlinks weekly-review
/backlinks spaced-repetition
/backlinks [[SomeEntity]]     # brackets optional
```

---

## Execution Steps

### Step 1 — Normalise entity name

Strip `[[` and `]]` if provided. Preserve original casing for display; use case-insensitive matching for the search.

### Step 2 — Search the KB

```bash
grep -rn "\[\[{entity}\]\]" . \
  --include="*.md" \
  --exclude-dir=".git" \
  --exclude-dir="node_modules"
```

Use case-insensitive flag (`-i`) so `[[ProjectAlpha]]` matches `[[projectalpha]]` variants.

### Step 3 — Build results

For each match:
- File path (relative to repo root)
- Line number
- One line of surrounding context (the sentence or bullet containing the link)

Group results by domain folder.

### Step 4 — Output

```
## Backlinks → [[{Entity}]]

Found N references across M files.

### daily-ops/ (N)
- `daily-ops/tasks/today.md:12` — "blocked by [[ProjectAlpha]] delivery"
- `daily-ops/reviews/2026-01-10.md:5` — "[[ProjectAlpha]] kicked off"

### second-brain/ (N)
- `second-brain/notes/project-alpha-notes.md:1` — "# [[ProjectAlpha]] Research"

### study/ (N)
...

### (root) (N)
- `CLAUDE.md:34` — "see [[ProjectAlpha]] for context"
```

If no results: `No [[wiki-link]] references found for "{{entity}}".`

---

## Alias Handling

If the entity has known aliases (e.g. full name and short name), you may pass multiple terms:

```
/backlinks EntityName AliasName
```

Results are merged and deduplicated.

---

## Use Cases

| Goal | Command |
|------|---------|
| Find all references to a project | `/backlinks ProjectName` |
| Find all references to a concept | `/backlinks spaced-repetition` |
| Find all references to a person | `/backlinks {{CONTACT_NAME}}` |
| Trace dependencies of a system file | `/backlinks goal-compass` |

---

## Configuration

| Setting | Location | Notes |
|---------|----------|-------|
| KB root | repo root | All `.md` files searched recursively |
| Excluded dirs | `.git`, `node_modules` | Adjust via grep flags if needed |

---

## Output Rules

- Grouped by domain — not a flat list.
- Context snippet on every match — not just file names.
- Count summary at the top.
- If > 20 results, truncate per domain to top 5 and note the total.
