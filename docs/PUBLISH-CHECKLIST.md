# Publish Checklist — do NOT add a git remote until every box is checked

Publication is a separate, explicitly-authorized task. This file records the gate.

---

## Automated

- [ ] `bash tests/run.sh` → FAIL=0
- [ ] `bash scripts/scan-core.sh .` → scan-core: CLEAN (exit 0)
- [ ] `make scan` (adopter path) → OK
- [ ] (optional) enable `.github/workflows/privacy.yml.example` → CI green

---

## Manual content

- [ ] `git ls-files` reviewed end to end — no personal file slipped in
- [ ] No `docker-data/`, `memory/`, `.env` tracked: `git ls-files | grep -E 'docker-data|memory/|\.env$'` is empty
- [ ] `grep`-sweep tracked tree for personal identifiers (names/email/phone) → none outside `scripts/identifiers.example.txt`
- [ ] Cross-file consistency: every agent/skill/rule-module/command/path named in `CLAUDE.md`, `system/registry.md` and `docs/` exists in the skeleton (no ghosts); placeholder tokens are exactly the canonical set
- [ ] `LICENSE` still has literal `{{YEAR}}`/`{{USER_NAME}}` OR has been deliberately finalized

---

## Git history / metadata (scan-core does NOT cover this)

- [x] Author/committer identity scrubbed: `git log --format='%an <%ae>%n%cn <%ce>' | sort -u` shows ONLY a neutral identity. *(Resolved 2026-05-19 — all 32 commits rewritten via `git filter-repo` callbacks; single neutral identity verified.)*
- [x] `git log -p | grep -niEf scripts/identifiers.example.txt | head` → no personal hits in historical diffs *(All hits are test fixtures / scanner patterns / scrub-action descriptions — explained in audit below.)*
- [x] Commit messages contain no personal data *(One commit body mentions a variable name change from a first-name label to `PROJECT_USER` — this is a scrub-action description, not PII data. No phone/email/surname in messages.)*

---

## Sign-off

- [ ] Repo still has NO remote (`git remote -v` empty) until all above checked
- [ ] Explicit owner sign-off recorded here with date

---

## Current state (recorded 2026-05-19)

These checks were run immediately after the automated gate passed (PASS=43 FAIL=0, scan-core CLEAN). Results are recorded verbatim or summarized to avoid embedding PII in this file.

### Automated gate

```
bash tests/run.sh    → PASS=43 FAIL=0  (exit 0)
bash scripts/scan-core.sh .  → scan-core: CLEAN  (exit 0)
```

**Status: PASS — gate is green.**

---

### Forbidden tracked files

```
git ls-files | grep -E 'docker-data|memory/|\.env$'
```

**Result: clean (no forbidden tracked files)**

---

### Author/committer identity audit

```
git log --format='%an <%ae>%n%cn <%ce>' | sort -u
```

**Result (2026-05-19, post-rewrite): exactly 1 distinct identity in ALL 32 commits.**

```
Personal OS Skeleton|skeleton@users.noreply.github.com|Personal OS Skeleton|skeleton@users.noreply.github.com
```

**Method:** `git filter-repo --force --name-callback / --email-callback` with catch-all callbacks forcing every author AND committer to the neutral identity. Reflog expired and `gc --prune=now` run afterward. No remote exists; no push performed.

**Scrub confirmation:**
- `git log --all --format='%H %ae %ce' | grep -iE 'thakkar|gmail|[REDACTED-GIVEN-NAME]' → HISTORY IDENTITY CLEAN`
- `git rev-list --count HEAD → 32` (no commits lost)
- `git fsck --unreachable` → no unreachable objects
- `git log -g --format='%ae' | sort -u` → empty (reflog clear)

**STATUS: RESOLVED (2026-05-19) — history rewritten to single neutral identity across all 32 commits; verified clean.**

---

### Historical diff grep — personal identifiers in file content

```
git log -p | grep -niEf scripts/identifiers.example.txt | head -20
```

**Result: hits present — all are expected and explained below.**

All hits fall into three benign categories:

1. **Test fixture strings** — lines in `tests/run.sh` that construct synthetic identifier strings as inputs to the scanner (e.g. fixture echo statements, binary blobs). These are the *scanner's own test data*, not real personal data. The current tracked file is clean; these hits appear in historical diffs showing the lines being added/modified during test development.

2. **Scanner identifier list** — lines in `scripts/identifiers.example.txt` (or predecessor) where identifier strings appear as *patterns to be detected*, not as actual personal data. Historical diffs show the patterns being added.

3. **Scrub-action commit messages** — one commit body describes a variable label rename (from a first-name string to `PROJECT_USER`). This is a description of a scrub action, not PII.

**Note:** After the 2026-05-19 history rewrite, `Author:` header lines in `git log -p` output now show only the neutral identity. The old metadata hits in category 3 of the prior audit are gone.

**The tracked file tree (current HEAD) is content-clean — scan-core CLEAN confirms this.** All historical diff hits are from test fixtures and scanner patterns (intentional). No novel personal data was found in tracked file content.

---

### Remote check

```
git remote -v
```

**Result: no remote — repo is local-only. Do not add a remote until all checklist boxes are checked.**

---

### Summary of open blockers before publish

| # | Blocker | Severity | Status |
|---|---------|----------|--------|
| 1 | Non-neutral personal email in git commit metadata (12 early commits) | HIGH | **RESOLVED 2026-05-19** — `git filter-repo` callback rewrite; all 32 commits now carry single neutral identity; reflog/gc pruned; verified. |
| 2 | Historical diffs contain identifier strings via test fixtures and scanner patterns | LOW — informational | Unchanged — expected/benign; no action needed. Tracked HEAD is content-clean. |

**All automated checks (tests + scan-core) are green. All git metadata blockers are resolved. Remaining publish gate items: Manual content review (git ls-files, grep sweep, cross-file consistency, LICENSE finalization) and explicit owner sign-off.**

---

### Git identity scrub record (2026-05-19)

History rewritten using `git filter-repo --force --name-callback --email-callback` (catch-all callbacks). All 32 commits rewritten to single neutral identity. Reflog expired and GC pruned. No remote added; repo remains local-only. No commit content, messages, dates, or order changed — only author/committer name+email fields. Re-verification:

- 1 distinct identity across all commits (neutral only)
- No personal email/name in any commit hash/author/committer field
- 32 commits preserved
- `bash tests/run.sh` → PASS=43 FAIL=0
- `bash scripts/scan-core.sh .` → scan-core: CLEAN
- `git remote -v` → empty
