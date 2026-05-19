---
name: focus
description: "Activates one or more domain contexts simultaneously so agents operate within those domains only. Accepts domain keys (ops, brain, study) or named combos (plan-week, deep-work, review, full). Use to scope the session before starting domain-specific work."
---

# Focus Mode (`/focus`)

## What This Skill Does

Sets `system/active-context.md` to declare which domains are active for this session.
Domain leads and agents read `active-context.md` to scope their responses — only active domains are surfaced.

## Invocation

```
/focus <domain-key | combo | off>
```

Multiple domain keys can be combined with `+`:

```
/focus ops
/focus ops+brain
/focus deep-work
/focus full
/focus off
```

---

## Domain Keys

| Key | Domain | Agents loaded |
|-----|--------|---------------|
| `ops` | Daily Ops | task, routine, review, wellbeing |
| `brain` | Second Brain | capture, organiser |
| `study` | Study | study, revision |

---

## Combos

| Combo | Domains | Use Case |
|-------|---------|----------|
| `plan-week` | ops + study | Weekly planning — tasks and learning |
| `deep-work` | study + brain | Focused study session |
| `review` | ops + brain | Daily/weekly review |
| `full` | all | Everything loaded |

---

## Execution Steps

### Step 1 — Parse input

Accept either:
- A single key or combo name
- A `+`-delimited list of keys

### Step 2 — Resolve domains

Map keys/combos to the canonical domain list. Unknown keys → error with suggestion.

### Step 3 — Write active-context

Update `system/active-context.md`:

```markdown
# Active Context

**Updated:** {YYYY-MM-DD HH:MM}
**Active domains:** {domain1}, {domain2}, ...
**Keys:** {key1}+{key2}

## Domain Index Refs
- daily-ops: `daily-ops/_index.md`
- second-brain: `second-brain/_index.md`
- study: `study/_index.md`
```

Only include sections for active domains.

### Step 4 — Load domain indexes

For each active domain, read `{domain}/_index.md` and summarise what is live.

### Step 5 — Confirm

Output:

```
Focus: {key(s)} active — {domain1}, {domain2}
{One-line summary of what each domain has loaded}
```

### `/focus off`

Clears `system/active-context.md` to "no active focus". All domains revert to default routing via master-orchestrator.

---

## How Agents Use Active Context

1. `master-orchestrator` reads `system/active-context.md` at session start.
2. Requests are routed only to active domain leads.
3. Domain leads skip indexes for inactive domains.
4. If `active-context.md` is absent or empty, all domains are accessible (default full routing).

---

## Configuration

| Setting | Location | Notes |
|---------|----------|-------|
| Active context file | `system/active-context.md` | Written by `/focus` |
| Domain indexes | `{domain}/_index.md` | Read on focus activation |
| Custom combos | `system/focus-combos.md` | Optional user-defined combos |

---

## Output Rules

- Confirmation in one or two lines.
- Show domain index summary only if a single domain is active (brevity).
- For `full` or 3+ domains, just confirm the key list — no index dump.
