---
name: lint
description: "Audits the markdown knowledge base for orphaned files, broken [[wiki-links]], stale dates, and structural issues. Classifies files as wiki nodes, log entries, or state files. Produces an actionable report. Use periodically to keep the KB healthy."
---

# KB Lint (`/lint`)

## What This Skill Does

Performs a full structural audit of the markdown KB, checking for:

1. **Orphaned files** — `.md` files not referenced by any `[[wiki-link]]` or index
2. **Broken `[[wiki-links]]`** — links that point to a file that does not exist
3. **Stale dates** — dated files or frontmatter older than a configurable threshold
4. **Missing index entries** — files in a domain folder not listed in `{domain}/_index.md`
5. **Empty files** — `.md` files with no content (or only frontmatter)

## Invocation

```
/lint [--fix] [path]
```

- No args → audit entire KB from repo root
- `--fix` → attempt auto-fixes for safe issues (see Fix Rules below)
- `path` → scope the audit to a subdirectory

---

## File Classification

Every `.md` file is classified into one of three types:

| Type | Criteria | Examples |
|------|----------|---------|
| **Wiki node** | Has `[[wiki-links]]` to/from other files; or is an entity/concept page | `second-brain/notes/*.md`, entity pages |
| **Log entry** | Filename is date-prefixed (`YYYY-MM-DD`) or contains a timestamp | `daily-ops/reviews/2026-01-15.md`, `second-brain/inbox/*.md` |
| **State file** | System/config file consumed by agents or slash commands | `system/*.md`, `*/_index.md`, `CLAUDE.md` |

Classification is used to tune orphan detection — log entries are expected to be standalone; wiki nodes should have backlinks.

---

## Execution Steps

### Step 1 — Index all files

```bash
find . -name "*.md" \
  --exclude-dir=".git" \
  --exclude-dir="node_modules" \
  | sort
```

Build a set of all `.md` file paths (relative).

### Step 2 — Extract all `[[wiki-links]]`

```bash
grep -rn "\[\[.*\]\]" . --include="*.md" -o
```

Parse each match to extract the linked entity/filename.
Build a map: `file → [links_out]` and `entity → [files_linking_in]`.

### Step 3 — Check for broken links

For each `[[LinkedEntity]]`:
- Attempt to resolve to a file: look for `{linked-entity}.md` or `{slug-of-entity}.md` in the KB.
- If not found → **broken link**.

### Step 4 — Check for orphans

For each wiki-node file:
- If it has zero backlinks AND is not referenced from any `_index.md` → **orphan candidate**.
- Log entries and state files are exempt from orphan checks.

### Step 5 — Check for stale dates

- For files with `date:` or `last_updated:` frontmatter: flag if older than 90 days (configurable).
- For dated-filename log entries: flag if older than 180 days with no linked wiki references.

### Step 6 — Check domain indexes

For each `{domain}/_index.md`:
- List files present in `{domain}/` (recursively).
- Identify files not mentioned in the index → **missing index entry**.

### Step 7 — Check empty files

Flag any `.md` file with < 3 non-whitespace lines of content.

### Step 8 — Produce report

```
## KB Lint Report — {YYYY-MM-DD}

### Summary
- Files scanned: N
- Broken [[wiki-links]]: N
- Orphaned wiki nodes: N
- Missing index entries: N
- Stale files: N
- Empty files: N

### Broken Links (N)
- `second-brain/notes/foo.md:12` → [[MissingEntity]] — no matching file found

### Orphaned Wiki Nodes (N)
- `second-brain/notes/old-idea.md` — 0 backlinks, not in _index

### Missing Index Entries (N)
- `daily-ops/habits/new-habit.md` not listed in `daily-ops/_index.md`

### Stale Files (N)
- `study/ai/notes/old-note.md` — last_updated: 2025-06-01 (>90d)

### Empty Files (N)
- `second-brain/inbox/2026-01-01-0000-draft.md` — 0 lines
```

If all checks pass: `KB Lint: CLEAN — {N} files checked, 0 issues`

---

## Fix Rules (`--fix`)

Safe auto-fixes only:

| Issue | Auto-fix |
|-------|----------|
| Empty inbox files | Delete if > 7 days old and 0 bytes |
| Missing index entry | Append a `- [[FileName]]` line to the domain `_index.md` |

Non-safe (require human decision):
- Broken links → report only; suggest candidates
- Orphans → report only; do not delete
- Stale files → report only; user decides

---

## Configuration

| Setting | Default | Notes |
|---------|---------|-------|
| Stale threshold (state/wiki) | 90 days | Configurable in `system/lint-config.md` |
| Stale threshold (logs) | 180 days | Configurable in `system/lint-config.md` |
| Excluded paths | `.git/`, `node_modules/`, `scripts/` | Always excluded |

---

## Output Rules

- Summary table first — counts at a glance.
- Detail sections only if count > 0.
- `CLEAN` message if nothing found — explicit green signal.
- `--fix` auto-fixes reported before the summary, with a list of changes made.
