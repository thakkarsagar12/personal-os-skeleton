---
# CRITICAL CONVENTION: `name` MUST be:
#   1. Unquoted (no quotes around the value)
#   2. kebab-case (lowercase, hyphens only — no spaces, no underscores)
#   3. Identical to the DIRECTORY name that contains this SKILL.md
#
# Example:
#   Directory: .claude/skills/weekly-review/
#   File:      .claude/skills/weekly-review/SKILL.md
#   name:      weekly-review          ← unquoted, kebab-case, matches directory
#
# Replace {{SKILL_NAME}} below with your actual kebab-case skill name.
name: {{SKILL_NAME}}
# Human-readable description — shown when the skill is listed.
# This value MAY be quoted if it contains special characters; the name: value must NOT be quoted.
description: "One-sentence description of what this skill does and when to use it."
---

<!-- ============================================================
  SKILL AUTHORING GUIDE
  This file is a copy-me template. Read the comments, fill in the
  sections, then delete all comment blocks.

  WHERE TO SAVE THIS FILE
  ========================
  .claude/skills/{{SKILL_NAME}}/SKILL.md
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  The directory name MUST equal the `name:` value in the frontmatter.
  If they diverge, the skill will not be found by the slash command.

  HOW SKILLS ARE INVOKED
  =======================
  The user types:  /{{SKILL_NAME}} [optional args]
  Claude Code loads this SKILL.md and executes the instructions.

  SKILL vs AGENT
  ==============
  • A SKILL is a recipe — it describes what steps to perform.
    It is stateless; it does not persist its own data.
  • An AGENT is a persistent persona with memory and a role.
    Use a skill when the task is bounded and repeatable.
    Use an agent when the task requires judgment across sessions.

  REGISTERING THIS SKILL
  =======================
  1. Save this file as `.claude/skills/{{SKILL_NAME}}/SKILL.md`
     ({{SKILL_NAME}} must be kebab-case and match `name:` above).
  2. Add it to the Skills table in the domain `_index.md`.
  3. Add it to the slash commands table in `CLAUDE.md`.
  ============================================================ -->

# {{SKILL_NAME}} (`/{{SKILL_NAME}}`)

<!-- Replace {{SKILL_NAME}} with the actual skill name in the heading above. -->

## What This Skill Does

<!-- 2-4 sentences. What problem does this solve? What output does it produce? -->

Describe the skill's purpose here. What does the user get at the end?

## Invocation

```
/{{SKILL_NAME}} [optional-arg]
```

<!-- Document every argument the skill accepts. If none, say "No arguments required." -->

| Argument | Required | Description |
|----------|----------|-------------|
| `arg-name` | No | What this arg does |

---

## Execution Steps

<!-- Number every step. Use bash blocks for commands. Keep steps atomic. -->

### Step 1 — Orientation

```bash
date    # confirm current date before any date-sensitive operations
```

Read the relevant domain `_index.md` to get the token-cheap summary of current state.

### Step 2 — Core Action

<!-- Describe the main work of the skill. -->

Read `{{DOMAIN_NAME}}/relevant-file.md`. Do the thing.

### Step 3 — Output

Render the result in the format below.

---

## Output Format

```
## {{SKILL_NAME}} — {YYYY-MM-DD}

### Section A
- Item 1
- Item 2

### Section B
Summary or action here.
```

---

## Configuration

<!-- Document every file or setting this skill depends on. -->

| Setting | Location | Notes |
|---------|----------|-------|
| Primary data | `{{DOMAIN_NAME}}/state-file.md` | What this file contains |
| Optional MCP | User's MCP config | Skipped silently when absent |

---

## Output Rules

- Short by default. Lead with the result.
- Bullets and headers, no walls of text.
- If a dependency is missing, skip it silently — do not error; note the absence once at most.
- One next action recommended at the end if the output is ambiguous.
