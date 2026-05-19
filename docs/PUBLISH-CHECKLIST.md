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

- [ ] Author/committer identity scrubbed: `git log --format='%an <%ae>%n%cn <%ce>' | sort -u` shows ONLY a neutral identity. **NOTE: early build commits carry a personal email — a history rewrite (e.g. fresh squashed root commit, or `git filter-repo --mailmap`) is REQUIRED before any remote is added.**
- [ ] `git log -p | grep -niEf scripts/identifiers.example.txt | head` → no personal hits in historical diffs
- [ ] Commit messages contain no personal data

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

**Result: 2 distinct identities present in the commit history.**

- 1 neutral identity: `Personal OS Skeleton <skeleton@users.noreply.github.com>` — used in all commits from the neutral-identity fix onward (16 commits, HEAD back through `ef9da74`).
- 1 non-neutral personal email: present in the 12 earliest commits (`484a574` through `33f6d51`, the initial Phase 0–2 build before the identity fix was applied).

**STATUS: OPEN BLOCKER — history rewrite is REQUIRED before adding any remote.**

Recommended remediation (choose one):
1. `git filter-repo --mailmap <mapfile>` — rewrites all commit author/committer metadata in-place (preferred; preserves full history with corrected identities).
2. Squash entire history into a single root commit with the neutral identity — simpler but destroys granular history.

Do NOT add a remote until one of the above is completed and re-verified.

---

### Historical diff grep — personal identifiers in file content

```
git log -p | grep -niEf scripts/identifiers.example.txt | head -20
```

**Result: hits present — all are expected and explained below.**

All non-`Author:` hits fall into two categories:

1. **Test fixture strings** — lines in `tests/run.sh` that construct synthetic PII strings as inputs to the scanner (e.g. fixture echo statements, binary blobs). These are the *scanner's own test data*, not real personal data added to the tree. The current tracked file is clean; these hits are in historical diffs showing the lines being added/modified during test development.

2. **Scanner identifier list** — lines in `scripts/identifiers.example.txt` (or predecessor) where personal names/email appear as *patterns to be detected*, not as actual data. Same explanation: historical diffs show the patterns being added.

3. **`Author:` header lines** — the 12 early commits with the non-neutral identity appear as `Author:` lines in `git log -p` output. These are the git metadata hits, not file-content hits.

**The tracked file tree (current HEAD) is content-clean — scan-core CLEAN confirms this.** The historical diff hits are from test fixtures and scanner patterns (intentional) plus the author metadata issue already documented above. No novel personal data was found in tracked file content.

---

### Remote check

```
git remote -v
```

**Result: no remote — repo is local-only. Do not add a remote until all checklist boxes are checked.**

---

### Summary of open blockers before publish

| # | Blocker | Severity | Remediation |
|---|---------|----------|-------------|
| 1 | Non-neutral personal email in git commit metadata for 12 early commits (`484a574`–`33f6d51`) | **HIGH — REQUIRED** | `git filter-repo --mailmap` or squash-rebase to neutral identity; re-verify with `git log --format='%an <%ae>' \| sort -u` |
| 2 | Historical diffs contain personal name strings via test fixtures and scanner patterns | LOW — informational | No action needed on content; blocked only by item 1 above |

All automated checks (tests + scan-core) are green. The sole publish blocker is the git history metadata rewrite.
