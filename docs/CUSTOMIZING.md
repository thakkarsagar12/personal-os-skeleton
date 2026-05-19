# Customizing Personal OS

How to personalize the skeleton after cloning — filling placeholders, enabling rule modules,
and tuning the system to fit your workflow.

---

## Placeholder Tokens

The skeleton ships with `{{PLACEHOLDER}}` tokens throughout its config files. Running
`/init-os` fills them interactively (one question at a time). You can also edit the files
directly.

### Token Reference

| Token | Where It Appears | What to Set |
|-------|-----------------|------------|
| `{{USER_NAME}}` | `CLAUDE.md`, agent files | Your name |
| `{{USER_ROLE}}` | `CLAUDE.md` | Your current role or title |
| `{{PROJECT_NAME}}` | `CLAUDE.md` | A name for your Personal OS instance |
| `{{NORTH_STAR}}` | `CLAUDE.md`, `system/goal-compass.md` | Your single overarching objective |
| `{{PILLAR_1}}` | `system/goal-compass.md` | Name of your first goal pillar |
| `{{PILLAR_2}}` | `system/goal-compass.md` | Name of your second goal pillar |
| `{{PILLAR_3}}` | `system/goal-compass.md` | Name of your third goal pillar |
| `{{PILLAR_4}}` | `system/goal-compass.md` | Name of your fourth goal pillar |
| `{{PILLAR_5}}` | `system/goal-compass.md` | Name of your fifth goal pillar |
| `{{TRACK_NAME}}` | `study/roadmap.template.md`, study index | Name of your first study track |
| `{{DOMAIN_NAME}}` | `_templates/domain/_index.md` | Replaced when creating a new domain |

### Filling Tokens via `/init-os`

```
/init-os
```

The command walks through every token interactively. After it completes, run:

```bash
make scan    # verify no personal data leaked into repo
```

### Filling Tokens Manually

Open the relevant file and do a find-and-replace. Tokens follow the pattern `{{TOKEN_NAME}}`.
After editing, verify with:

```bash
grep -rn '{{' CLAUDE.md system/goal-compass.md   # check for unfilled tokens
```

---

## Enabling Rule Modules

Rule modules are opt-in behaviors that persist across every conversation. They are all
**disabled by default**. The four built-in modules live in `system/rules/`.

### How to Enable a Module

Open `system/rules.md` and change the `Enabled` column for the module from
`disabled by default` to `enabled`:

**Before:**
```markdown
| `system/rules/elimination.md` | Caps weekly active priorities; overflows to backlog | disabled by default |
```

**After:**
```markdown
| `system/rules/elimination.md` | Caps weekly active priorities; overflows to backlog | enabled |
```

The master-orchestrator and domain leads read `system/rules.md` at session start. The change
takes effect in the next conversation.

You can also enable modules during `/init-os` — it will prompt you for each one.

### Built-in Modules

| Module File | What It Does | Enable When |
|-------------|-------------|------------|
| `system/rules/elimination.md` | Caps weekly active priorities; excess goes to `daily-ops/tasks/backlog.md` | You have too many concurrent priorities |
| `system/rules/wellbeing-calibrator.md` | Prompts an energy/stress self-rating; adapts task load accordingly | You want context-aware task pacing |
| `system/rules/spaced-repetition.md` | Spaced repetition schedule (standard intervals) for study topics | You use the Study domain actively |
| `system/rules/date-awareness.md` | Verifies current date at session start; prevents stale date assumptions | Always recommended |

### Adding a Custom Rule Module

1. Create `system/rules/your-rule-name.md` using the same structure as the existing modules.
2. Add a row to the Module Index table in `system/rules.md`.
3. Set it to `enabled` in the table when you want it active.

Rule files should be self-contained — describe exactly what to do and when, without
depending on personal data that is not defined as a placeholder.

---

## Configuring the Goal Compass

`system/goal-compass.md` is the north-star file. Fill in after `/init-os`:

1. Replace `{{NORTH_STAR}}` with your single overarching objective.
2. Replace `{{PILLAR_1}}` through `{{PILLAR_5}}` with your five goal pillars.
3. Fill in the Pillar ↔ Domain Mapping table to link pillars to the three skeleton domains.
4. Add concrete milestones at the bottom.

The `morning` and `evening` skills reference this file for the daily alignment check
("which pillar am I pushing today?"). The `weekly-review` skill checks which pillars moved
and which were neglected.

---

## Configuring the Study Domain

The study domain supports named **tracks** — independent learning threads (e.g., `python`,
`system-design`, `data-structures`).

**Set your first track:**

1. Replace `{{TRACK_NAME}}` in `study/roadmap.template.md` and `study/_index.md`.
2. Create the track directory: `mkdir -p study/{track-name}/notes study/{track-name}/cards`
3. Copy `study/roadmap.template.md` to `study/{track-name}/roadmap.md` and fill it in.

**Add a second track:**

1. Copy `study/roadmap.template.md` to `study/{new-track}/roadmap.md`.
2. Create the directory structure as above.
3. Register the track in `study/_index.md`.

Roadmap items use standard checkbox syntax:
- `[ ]` — not started
- `[~]` — in progress
- `[x]` — complete

---

## Adding Domains

To add a domain beyond the three that ship with the skeleton, see [EXTENDING.md](EXTENDING.md).
The short version:

1. Copy `_templates/domain/_index.md` to `{domain-name}/_index.md`.
2. Create a lead agent and at least one specialist agent.
3. Register in `system/registry.md`, `system/active-context.md`, `CLAUDE.md`, and
   `master-orchestrator.md`.
4. Work through the Register-Me checklist in the domain `_index.md`.

---

## Focus Combos

Built-in combos are defined in `CLAUDE.md` and `system/active-context.md`. To add a custom
combo:

1. Open `system/active-context.md` and add a row to the combos table.
2. Open `CLAUDE.md` and add a row to the Focus System combos table.

Example custom combo entry:

```markdown
| `create` | brain + study | Generate content from recent learning |
```

---

## Communication Style

Core communication behaviors are baked into `CLAUDE.md` and apply to all agents:

- One question at a time — never multiple questions in a single message.
- Lead with the answer. Short by default.
- Bullets and tables over prose.

These are **not** rule modules — they cannot be disabled via `system/rules.md`. If you want
different defaults, edit the Communication Rules section of `CLAUDE.md` directly.

---

## Privacy Configuration

`scripts/identifiers.txt` controls what the privacy scanner flags. It is git-ignored and
must be created locally:

```bash
cp scripts/identifiers.example.txt scripts/identifiers.txt
# Edit identifiers.txt — add your real name, email, phone, and any other PII
```

Run the scanner any time before sharing or pushing:

```bash
make scan                        # full privacy scan
bash scripts/scan-core.sh docs   # scan a specific directory
```

---

## After Customizing

Once you have personalized the system, run the full health check:

```bash
make doctor    # infra + config diagnostics
make scan      # privacy scan
make test      # test suite (expect PASS=35 FAIL=0)
```

If all three pass, your Personal OS is ready for daily use.
