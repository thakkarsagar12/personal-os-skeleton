# Recommended Tooling

Optional external tools that integrate well with Personal OS. None of these are vendored
into the skeleton — they are **referenced, not bundled**. Each section states WHAT the tool
is, HOW to install it, and WHY it is optional rather than required.

---

## Tools Shipped Natively

These two capabilities are already inside the skeleton — no external installation needed.

### Repo RAG (`system/db/repo_index.py`)

**WHAT:** Semantic search over your own markdown knowledge base. Chunks every `.md` file by
H2 heading, stores embeddings in Qdrant, and lets you find relevant sections with a natural
language query.

**HOW TO USE:**

```bash
# Full (re)index — run after adding many files
python system/db/repo_index.py index

# Incremental — only files changed in the last 24 hours
python system/db/repo_index.py index --changed-since 24

# Search
python system/db/repo_index.py search "your question in natural language"
python system/db/repo_index.py search "query" --domain study --top 3

# Stats
python system/db/repo_index.py status
```

**WHY OPTIONAL:** The skeleton works fine with direct file reads. RAG becomes valuable once
you have hundreds of notes and no longer remember where things live. Enable it when the KB
grows large enough that "where did I write about X?" becomes a real friction point.

---

### Obsidian-Wiki Pattern (`[[links]]` + `/backlinks` + `/lint`)

**WHAT:** A graph-style linking convention where `[[EntityName]]` in any markdown file
creates a directed reference. The `/backlinks` and `/lint` skills scan the whole KB for
these links, giving you orphan detection, broken-link reports, and a way to trace what
references a given concept.

**HOW TO USE:** No installation. Just use `[[EntityName]]` in your markdown files instead
of `[text](path)` for internal links. Then:

```
/backlinks ProjectAlpha          # find everything that references this entity
/lint                            # full KB audit
/lint --fix                      # auto-fix safe issues
```

**WHY OPTIONAL:** Plain markdown with no `[[...]]` links still works. The pattern adds most
value once you have interconnected notes (e.g., a project referenced from tasks, study
notes, and captures) and want to trace those connections.

---

## External Tools

### graphify — Knowledge Graph Visualisation

**WHAT:** A Claude Code skill that converts any input (code, docs, markdown, images, papers)
into a clustered knowledge graph rendered as interactive HTML. Useful for visualising how
your KB concepts connect.

**INSTALL:** Add the skill to your Claude Code installation per the upstream instructions.
The skill is invoked with `/graphify` inside Claude Code.

**WHY OPTIONAL:** Purely a visualisation layer. Personal OS works without it. Use it when
you want to see the graph structure of a domain or trace relationships between entities
across the KB.

---

### claude-mem — Session Capture Plugin

**WHAT:** A Claude Code plugin that automatically records every session into a local SQLite
database (`~/.claude-mem/claude-mem.db`). The skeleton ships a bridge (`system/db/bridge.py`)
that mirrors those records nightly (and on session end via Stop hook) into the local
Postgres + Qdrant stores, giving you searchable conversation history.

**INSTALL:** Install as a Claude Code MCP plugin per the claude-mem upstream documentation.
Once installed, it runs transparently in the background — no commands needed.

**HOW THE BRIDGE WORKS:**

```bash
python system/db/bridge.py status      # show watermark + record counts
python system/db/bridge.py sync        # incremental sync (since watermark)
python system/db/bridge.py sync --backfill   # sync from epoch 0 (first run / gap fill)
```

Configure which project labels to sync by editing `PROJECTS` in `bridge.py`.

**PRIVACY HAZARD — READ THIS BEFORE SHARING YOUR FORK:**

> **NEVER commit `docker-data/` or `memory/` directories.** These directories contain your
> actual conversation history and database files. They are excluded from the skeleton's
> `.gitignore` by default — do not override that.

Additionally:
- **Do not commit `~/.claude-mem/`** contents. The SQLite database lives in your home
  directory and is outside the repo, but any exports or backups you copy into the repo
  must be excluded.
- Before pushing or sharing your fork, always run `make scan` (which calls
  `scripts/make-shareable.sh`) to verify no personal data has leaked into tracked files.

```bash
make scan    # expect: scan-core: CLEAN
```

**WHY OPTIONAL:** The skeleton's memory DB works without claude-mem — you can log sessions
manually via `python system/db/memory.py smart-start`. claude-mem eliminates the manual
step and captures every session automatically, including sessions where you forget to log.

---

### andrej-karpathy-skills — Coding Guidelines Skill

**WHAT:** A Claude Code skill set inspired by Andrej Karpathy's coding principles. Adds a
`/karpathy-guidelines` skill that applies opinionated, practical coding guidelines (clear
naming, minimal abstraction, readable-by-default code) to any code you are working on.

**INSTALL:** Available at:

```
https://github.com/multica-ai/andrej-karpathy-skills
```

MIT licensed. Follow the installation instructions in that repository to add the skill to
your Claude Code setup.

**WHY OPTIONAL:** Personal OS is a markdown knowledge base — most of its automation is
agent prompts, not production code. This skill is most useful if you extend the skeleton
with custom Python scripts (e.g., new `system/db/` utilities) or use Personal OS alongside
a software project.

---

## Integration Notes

All external tools listed above follow the same pattern relative to the skeleton:

1. They are installed separately — no changes to the skeleton's tracked files are required.
2. The skeleton's privacy scanner (`scripts/scan-core.sh`) is unaware of external tool
   state — it only scans tracked repo files. Always verify external tool outputs (exports,
   backups, generated files) before committing them.
3. MCP integrations (Google Calendar, Gmail, etc.) are configured via your Claude Code
   MCP settings, not inside this repo.

---

## Privacy Reminder

Before committing or sharing your fork:

```bash
make scan    # privacy scan
bash scripts/scan-core.sh .    # direct scanner call
```

Populate `scripts/identifiers.txt` (copy from `scripts/identifiers.example.txt`) with your
real names, email addresses, phone numbers, and any other personal identifiers. The scanner
uses this file to catch leaks specific to your setup.
