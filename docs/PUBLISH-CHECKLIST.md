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

- [x] Author/committer identity scrubbed: `git log --format='%an <%ae>%n%cn <%ce>' | sort -u` shows ONLY a neutral identity. *(Resolved 2026-05-19 — all commits rewritten via `git filter-repo` callbacks; single neutral identity verified after both scrub passes.)*
- [x] `git log -p | grep -niEf scripts/identifiers.example.txt | head` → no personal hits in historical diffs *(All hits are test fixtures / scanner patterns — explained in audit below.)*
- [x] Commit messages contain no personal data *(Second scrub pass 2026-05-19: a commit body previously contained a personal first-name token in a code-label description. **A real personal name in a commit message IS PII** — exposed by `git log` on any clone — so the earlier "not PII" framing was incorrect. The token was scrubbed via a `git filter-repo --message-callback` pass that case-insensitively replaces the full personal name/email/path/phone token set with neutral equivalents while preserving message meaning and `Co-Authored-By` trailers. Verified: zero personal tokens remain in any commit subject or body.)*

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

Remaining hits fall into two benign categories:

1. **Test fixture strings** — lines in `tests/run.sh` that construct synthetic identifier strings as inputs to the scanner (e.g. fixture echo statements, binary blobs). These are the *scanner's own test data*, not real personal data. The current tracked file is clean; these hits appear in historical diffs showing the lines being added/modified during test development.

2. **Scanner identifier list** — lines in `scripts/identifiers.example.txt` (or predecessor) where identifier strings appear as *patterns to be detected*, not as actual personal data. Historical diffs show the patterns being added.

**Correction (2026-05-19, second pass):** A prior revision of this audit listed a third "benign" category — a commit body that named a personal first-name token while describing a code-label rename — and dismissed it as "a description of a scrub action, not PII." **That characterization was wrong.** A real personal name embedded in a commit message is PII, fully exposed by `git log` / `git log -p` on any clone of the repository, independent of file content. It was remediated by a second `git filter-repo --message-callback` pass (see scrub record below) that scrubbed the full personal token set from all commit messages. Zero personal tokens now remain in any commit subject or body.

**Note:** After the history rewrites, `Author:` / committer header lines in `git log -p` output show only the neutral identity. The old metadata hits from the pre-rewrite audit are gone.

**The tracked file tree (current HEAD) is content-clean — scan-core CLEAN confirms this.** All remaining historical diff hits are from test fixtures and scanner patterns (intentional). No novel personal data was found in tracked file content.

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
| 1 | Non-neutral personal email/name in git commit author+committer metadata (early commits) | HIGH | **RESOLVED 2026-05-19** — `git filter-repo` callback rewrite (pass 1); all commits carry single neutral identity; reflog/gc pruned; verified. |
| 2 | Personal first-name token in a commit message body (PII via `git log` on any clone) | **HIGH** | **RESOLVED 2026-05-19** — `git filter-repo --message-callback` rewrite (pass 2); full personal name/email/path/phone token set scrubbed from all commit messages case-insensitively; `Co-Authored-By` trailers preserved; verified MESSAGES CLEAN + single neutral identity re-asserted. |
| 3 | Historical diffs contain identifier strings via test fixtures and scanner patterns | LOW — informational | Unchanged — expected/benign; no action needed. Tracked HEAD is content-clean. |

**All automated checks (tests + scan-core) are green. All git metadata AND commit-message PII blockers are resolved. Remaining publish gate items: Manual content review (git ls-files, grep sweep, cross-file consistency, LICENSE finalization) and explicit owner sign-off.**

---

### Git identity scrub record (2026-05-19)

**Pass 1 — identity metadata.** History rewritten using `git filter-repo --force --name-callback --email-callback` (catch-all callbacks). All commits rewritten to single neutral identity. Reflog expired and GC pruned. No remote added; repo remains local-only. No commit content, dates, or order changed — only author/committer name+email fields.

**Pass 2 — commit messages (this update).** A second `git filter-repo --force --message-callback` pass (re-asserting the same neutral name/email callbacks so identity stays forced) scrubbed the full personal token set from ALL commit messages, case-insensitively: personal email → `USER_EMAIL`; `/Users/<name>` paths → `$PERSONAL_OS_ROOT`; quoted first-name code-label → `"PROJECT_USER"`; phone → `REDACTED`; surname → dropped; remaining personal name tokens → `the-user`. `Co-Authored-By: ... <noreply@anthropic.com>` trailers preserved verbatim. Messages remain meaningful and otherwise intact. Reflog expired and GC pruned again.

Re-verification (both passes, recorded without embedding literal PII):

- Exactly 1 distinct identity across all commits: `Personal OS Skeleton <skeleton@users.noreply.github.com>` (author + committer)
- No personal email/name in any commit author/committer field
- No personal name/email/path/phone token in any commit subject or body — `MESSAGES CLEAN`
- Raw commit-object sweep → `OBJECT IDENTITY CLEAN` (only neutral + Anthropic noreply)
- `git for-each-ref` → only `refs/heads/main` (no `refs/original` / `refs/replace`)
- `git fsck --unreachable --no-reflogs` → none
- All commits preserved (count below); head/tail order coherent
- `bash tests/run.sh` → PASS=43 FAIL=0
- `bash scripts/scan-core.sh .` → scan-core: CLEAN
- `git remote -v` → empty (no remote; no push performed)
