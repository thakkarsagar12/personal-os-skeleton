---
domain: {{DOMAIN_NAME}}
---

# {{DOMAIN_NAME}} — Index

<!-- Replace {{DOMAIN_NAME}} with the lowercase kebab-case name of your new domain (e.g. finance, health, career). -->

One-sentence description of what this domain covers.

**Always read this file first** before diving into subdirectory files — it is the token-cheap summary of what is live in this domain.

---

## Subdirectories

<!-- List every subdirectory in this domain and its purpose. -->

| Path | Purpose |
|------|---------|
| `{{DOMAIN_NAME}}/subdir-a/` | What goes here |
| `{{DOMAIN_NAME}}/subdir-b/` | What goes here |

---

## Active State

<!-- Files that reflect the CURRENT state of this domain (tasks, tracker grids, inboxes).
     Agents should read these first when "what is happening now" is the question. -->

| File | Class | Purpose |
|------|-------|---------|
| `{{DOMAIN_NAME}}/state-file.md` | STATE | One-line description of what live data is here |

---

## Agents

<!-- List the domain lead and its specialist agents.
     All agents must be created in .claude/agents/<agent-name>.md. -->

| Agent | Role |
|-------|------|
| `{{DOMAIN_NAME}}-lead` | Domain lead — coordinates all {{DOMAIN_NAME}} specialists |
| `{{DOMAIN_NAME}}-agent` | Specialist — describe the focus area |

---

## Skills

<!-- List every slash command that belongs to this domain.
     Each skill must be created in .claude/skills/<skill-name>/SKILL.md. -->

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `/{{DOMAIN_NAME}}-skill` | `/{{DOMAIN_NAME}}-skill [args]` | What it does |

---

## Freshness Rules

<!-- Define staleness conditions so agents know when to flag outdated data. -->

- State files must be reviewed at least weekly — else the domain lead flags them on next run.
- Completed items should be archived to keep active lists short.

---

## Linked Systems

<!-- Cross-domain dependencies. Keep this list minimal; each link is a coupling. -->

- Goal compass → `system/goal-compass.md` (if pillar tracking is enabled)
- Behavior patterns → `system/behavior-log.md` (read at session start)

---

## Register-Me Checklist

<!-- Complete every item in this list to fully wire the new domain into the system. -->

- [ ] **Add to `system/registry.md`** — append the domain row to the domains table
- [ ] **Create domain lead agent** — copy `_templates/agent.template.md` to `.claude/agents/{{DOMAIN_NAME}}-lead.md`; set `name: {{DOMAIN_NAME}}-lead`
- [ ] **Create specialist agent(s)** — one `.claude/agents/<specialist>.md` per specialist; wire them under the lead
- [ ] **Add focus key to `system/active-context.md`** — pick a short key (e.g. `{{DOMAIN_NAME}}`) and add it to the active-context domain list
- [ ] **Add focus key to `CLAUDE.md` Focus System table** — document the key and its combos
- [ ] **Wire under master-orchestrator** — add the lead to the routing table in `.claude/agents/master-orchestrator.md`
- [ ] **Create at least one skill** — copy `_templates/skill.template.md` to `.claude/skills/<skill-name>/SKILL.md`; register it in this `_index.md` skills table
- [ ] **Create the directory structure** — `mkdir -p {{DOMAIN_NAME}}/` with the subdirs listed above
- [ ] **Delete this checklist** — once all items are ticked, remove the Register-Me section from this file
