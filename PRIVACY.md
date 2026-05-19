# PRIVACY.md — Discipline Propagation Guide

This document explains the privacy model for this skeleton and **what you must do** to keep your fork clean before sharing it.

---

## 1. Allowlist philosophy

This skeleton was built by **copying only known-safe files** from a private source repo — never by scrubbing or redacting a personal repository after the fact.

That discipline matters: scrubbing is error-prone. A single missed file, a stale git object, or a log entry can leak data you thought you removed. The allowlist approach starts with an empty tree and adds only files that were reviewed and confirmed safe.

**Forks must keep the same discipline.** When you extend this skeleton with personal content:

- Add personal data deliberately, file by file, knowing each file is private to your machine.
- Never copy an entire personal repo into your fork and rely on the scanner to catch everything.
- Keep the scanner as a safety net, not as your primary guard.

---

## 2. The claude-mem hazard

If you enable the `claude-mem` MCP server, it captures every Claude Code session into `~/.claude-mem/claude-mem.db` on your local machine. If you also run the optional memory bridge (`system/db/bridge.py`), it mirrors that data into a Postgres + Qdrant stack under `docker-data/` inside this repo.

**Never commit these paths:**

| Path | What it contains |
|------|-----------------|
| `docker-data/` | Postgres and Qdrant volumes — full conversation history |
| `memory/` | Session memory exports |
| `.env` | Database credentials and API keys |
| `*.log` | Application logs, which may include conversation fragments |

The `.gitignore` in this skeleton already excludes these paths. **Verify that `.gitignore` is in place before your first commit after enabling claude-mem.**

The pre-push git hook (`scripts/scan-core.sh`) will also block a push if these paths appear in the working tree, but the hook fires at push time — you want to catch this earlier.

---

## 3. MANDATORY: run `make scan` before sharing

Before you publish, push to a public remote, or share your fork with anyone, run:

```bash
make scan
# equivalent: bash scripts/make-shareable.sh
```

This runs `scripts/scan-core.sh` against the entire repo tree and checks for:

1. **Denylisted paths** — `docker-data/`, `memory/`, `.env`, `*.log`, `personal-sessions/`, `secrets/`, `vault/` (see `scripts/denylist.txt`)
2. **Identifier matches** — any text matching the regexes in `scripts/identifiers.txt` (or `scripts/identifiers.example.txt` if you have not created your own)

The scan must exit clean before you share:

```
scan-core: CLEAN
```

### Pre-push git hook

`make init` (run during setup) installs a pre-push hook at `.git/hooks/pre-push` that runs `scan-core.sh` automatically before every `git push`. If the scan fails, the push is blocked.

### Optional CI enforcement

The file `.github/workflows/privacy.yml.example` contains a GitHub Actions workflow that runs the scan on every push and pull request. Rename it to `privacy.yml` to enable it in your fork.

---

## 4. Set YOUR identifiers

The scanner uses `scripts/identifiers.txt` to match personal data. The default file (`scripts/identifiers.example.txt`) contains placeholder regexes that were relevant to this skeleton's source; **they do not cover your data**.

Set up your own identifier file:

```bash
cp scripts/identifiers.example.txt scripts/identifiers.txt
# Then edit scripts/identifiers.txt
```

Add POSIX ERE regexes (one per line) for:

- Your full name and any common short forms
- Your email address(es)
- Your phone number(s)
- Names of family members, employers, clients
- Any other personally identifying strings

**Important notes:**

- Use POSIX ERE only. BSD `grep` (macOS) silently ignores PCRE escapes like `\b` and `\d`. Use character classes instead: `[0-9]{10}` not `\d{10}`.
- `scripts/identifiers.txt` is already listed in `.gitignore` — it stays local to your machine.
- The example file (`scripts/identifiers.example.txt`) IS tracked by git; it contains only generic placeholder patterns, not real data.

---

## 5. Limitations — git history and metadata

The scanner checks the **working tree** — the files currently on disk. It does **not** scan:

- Git history (previous commits may contain data that `git log`, `git show`, or `git clone` will expose)
- Git metadata (author name, email in commits, tag messages)
- Packed objects or refs in `.git/`

If your fork has a history that includes personal data, you must rewrite that history before going public:

```bash
# Set a neutral author for all future commits
git config user.name "{{YOUR_PUBLIC_NAME}}"
git config user.email "{{YOUR_PUBLIC_EMAIL}}"

# To rewrite existing history, use git-filter-repo (preferred) or BFG Repo Cleaner.
# This is a destructive operation — back up your repo first.
# git-filter-repo: https://github.com/newren/git-filter-repo
```

This skeleton's own commit history was built from a clean tree (allowlist approach, point 1), so its history is safe. History in your fork is your responsibility.

---

## Summary checklist before sharing

- [ ] `make scan` exits clean (`scan-core: CLEAN`)
- [ ] `scripts/identifiers.txt` contains YOUR identifiers (not just the example placeholders)
- [ ] `docker-data/`, `memory/`, `.env` are not present in the working tree
- [ ] Git commit author is set to the identity you want to expose publicly
- [ ] Git history does not contain personal data (rewrite with git-filter-repo if needed)
- [ ] `.github/workflows/privacy.yml.example` renamed to `privacy.yml` if you want CI enforcement
