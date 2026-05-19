# Extending the System

How to add new domains, agents, and skills to Personal OS. Each procedure references the
real template scaffolds in `_templates/` and the registration steps required to wire the
new component into the live system.

---

## 1. Add a Domain

A **domain** is a new top-level area of your life (e.g., `finance`, `health`, `career`).
Each domain gets a folder, a `_index.md`, a domain lead agent, at least one specialist
agent, and a focus key.

### Step-by-step

**1. Create the directory structure**

```bash
mkdir -p {domain-name}/tasks   # or whatever subdirs make sense
```

Use `kebab-case` for the folder name (e.g., `finance`, `health`, `my-projects`).

**2. Create the domain `_index.md`**

Copy the template:

```bash
cp _templates/domain/_index.md {domain-name}/_index.md
```

Fill in `{{DOMAIN_NAME}}` and the subdirectory table. This file is the token-cheap entry
point that agents read before anything else in the domain.

**3. Create the domain lead agent**

```bash
cp _templates/agent.template.md .claude/agents/{domain-name}-lead.md
```

In the frontmatter:
- Set `name: {domain-name}-lead` (must match the filename, unquoted, kebab-case)
- Set `model: opus`
- Add `Task` to the `tools:` list (leads spawn specialists)

Read the authoring guide comments in the template carefully, then delete them.

**4. Create at least one specialist agent**

```bash
cp _templates/agent.template.md .claude/agents/{domain-name}-agent.md
```

In the frontmatter:
- Set `name: {domain-name}-agent`
- Set `model: sonnet`
- Do NOT add `Task` unless this specialist spawns further sub-agents

Wire it under the lead: add it to the routing table in `.claude/agents/{domain-name}-lead.md`.

**5. Register in `system/registry.md`**

Add a row to the Domains table and rows to the Agent Definitions table for both the lead
and the specialist(s).

**6. Add a focus key to `system/active-context.md`**

Pick a short key (e.g., `finance`) and add it to the Available Domains table. Document which
agents are activated.

**7. Wire under master-orchestrator**

Add the new lead to the routing table in `.claude/agents/master-orchestrator.md`. Define
which request types route to this lead.

**8. Update `CLAUDE.md`**

- Add the domain to the Architecture table.
- Add the focus key and any combos to the Focus System table.
- Add any new slash commands to the Slash Commands table.

**9. Create at least one skill**

See "Add a Skill" below.

**10. Tick the Register-Me checklist**

The `_templates/domain/_index.md` contains a Register-Me Checklist. Work through it and
delete the checklist section once all items are ticked.

---

## 2. Add an Agent

Use this procedure when you want to add a specialist agent to an existing domain (or a new
lead for a new domain — the steps are the same, with the model/tools differences noted).

**1. Copy the template**

```bash
cp _templates/agent.template.md .claude/agents/{agent-name}.md
```

**2. Fill in the frontmatter**

| Field | Specialist | Lead |
|-------|-----------|------|
| `name` | `{agent-name}` (kebab-case, unquoted, matches filename) | same |
| `model` | `sonnet` | `opus` |
| `tools` | `Read, Write, Edit, Grep, Glob, Bash` | add `Task` |

**3. Write the agent body**

Follow the Orchestrator → Lead → Specialist contract described in the template:
- State who spawns this agent.
- List 3–5 concrete responsibilities.
- Document the files it reads and writes.
- Enumerate capabilities and hard constraints.

Delete all comment blocks before saving.

**4. Wire it into its parent**

Add the agent to its parent's routing table:
- Specialist → add to `.claude/agents/{domain-name}-lead.md`
- New lead → add to `.claude/agents/master-orchestrator.md`

**5. Register**

Add a row to the Agent Definitions table in `system/registry.md`.

**6. Update the domain `_index.md`**

Add the agent to the Agents table in `{domain-name}/_index.md`.

---

## 3. Add a Skill

A **skill** is a slash command — a bounded, repeatable recipe. Skills are stateless; they
describe what steps Claude should perform when invoked.

**1. Create the skill directory and file**

```bash
mkdir -p .claude/skills/{skill-name}
cp _templates/skill.template.md .claude/skills/{skill-name}/SKILL.md
```

The directory name **must** equal the `name:` value in the frontmatter (kebab-case, unquoted).

**2. Fill in the SKILL.md**

- Set `name: {skill-name}` in frontmatter.
- Document what the skill does, its arguments, numbered execution steps, and output format.
- Delete the authoring guide comment blocks.

**3. Register the skill**

- Add it to the Skills table in `system/registry.md`.
- Add a row to the Slash Commands table in `CLAUDE.md`.
- Add it to the Skills table in the relevant domain `_index.md`.

---

## Wiki-Link Convention

Personal OS uses `[[WikiLink]]` syntax as its internal linking standard. This is the
**Obsidian-wiki pattern** — any `[[EntityName]]` in a markdown file creates a directed
reference from that file to the entity named.

### Rules

- Use `[[EntityName]]` to link from one markdown file to another concept, project, person,
  or note. The entity name typically corresponds to a file (e.g., `[[ProjectAlpha]]` →
  `second-brain/notes/project-alpha.md`).
- Links are case-insensitive for resolution but preserve original casing for display.
- Do NOT use standard Markdown `[text](path)` for internal KB links — use `[[...]]` only,
  so `/backlinks` and `/lint` can scan them.

### File Classification

The `/lint` skill classifies every `.md` file into one of three types:

| Type | Criteria | Examples |
|------|----------|---------|
| **Wiki node** | Has `[[wiki-links]]` to/from other files; or is a concept/entity page | `second-brain/notes/*.md` |
| **Log entry** | Filename is date-prefixed (`YYYY-MM-DD`) or contains a timestamp | `daily-ops/reviews/2026-01-15.md` |
| **State file** | System/config file consumed by agents or slash commands | `system/*.md`, `*/_index.md` |

Classification governs orphan detection:
- Log entries are expected to be standalone — not flagged as orphans.
- Wiki nodes without backlinks and not in any `_index.md` are flagged as orphan candidates.
- State files are exempt from orphan checks.

### Related Commands

| Command | What it does |
|---------|-------------|
| `/backlinks [[EntityName]]` | Lists every file that contains `[[EntityName]]` with context snippets |
| `/lint` | Full KB audit — broken links, orphans, stale dates, missing index entries |
| `/lint --fix` | Auto-fixes safe issues (empty inbox files, missing index entries) |

---

## Extending Rule Modules

See [CUSTOMIZING.md](CUSTOMIZING.md) for how to enable existing rule modules and how to add
custom rules beyond the four built-in modules.

---

## Checklist Summary

| Task | Key files touched |
|------|-----------------|
| Add domain | `{domain}/_index.md`, `.claude/agents/{domain}-lead.md`, `.claude/agents/{domain}-agent.md`, `system/registry.md`, `system/active-context.md`, `CLAUDE.md`, `master-orchestrator.md` |
| Add agent | `.claude/agents/{agent}.md`, parent lead, `system/registry.md`, domain `_index.md` |
| Add skill | `.claude/skills/{skill}/SKILL.md`, `system/registry.md`, `CLAUDE.md`, domain `_index.md` |
