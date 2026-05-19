---
name: capture
description: "Instantly saves a note, idea, link, or thought to second-brain/inbox/ with a timestamp. Zero friction — do not organise, just capture. Use any time you have something to save before it's lost."
---

# Quick Capture (`/capture`)

## What This Skill Does

Saves any free-text input immediately to `second-brain/inbox/` with a datestamp.
No organising, tagging, or decisions required at capture time — that is the organiser agent's job later.

## Invocation

```
/capture <text>
```

**Examples:**

```
/capture idea: build a CLI tool for KB search
/capture link: https://example.com/interesting-article
/capture note: the meeting clarified the deadline is next Friday
/capture follow up with Alex about the API proposal
```

---

## Execution Steps

### Step 1 — Receive input

The full text after `/capture` is the capture content. Accept any format: sentence, URL, bullet, multi-line.

### Step 2 — Generate filename

```
{YYYY-MM-DD}-{HHmm}-{slug}.md
```

Where `slug` is the first 4–6 meaningful words of the capture, lowercased, hyphenated.

Example: `2026-01-15-0934-idea-cli-tool-kb-search.md`

### Step 3 — Write file

Path: `second-brain/inbox/{filename}.md`

File content:

```markdown
---
captured: {YYYY-MM-DD HH:MM}
type: inbox
---

{Full capture text, verbatim}
```

### Step 4 — Confirm

Output a single line:

```
Captured → second-brain/inbox/{filename}.md
```

---

## Organiser Pipeline

Inbox files are periodically processed by the `organiser-agent`:
- Files are triaged and moved to the appropriate domain folder
- Tags and backlinks are added during triage
- Inbox is not a permanent home — it is a landing zone

To trigger manual triage: invoke the `second-brain-lead` agent directly.

---

## Configuration

| Setting | Location | Notes |
|---------|----------|-------|
| Inbox path | `second-brain/inbox/` | Auto-created if absent |
| Triage rules | `second-brain/organiser-rules.md` | Optional; guides organiser-agent |

---

## Output Rules

- One confirmation line only.
- No questions, no elaboration.
- Never lose the capture — if the file write fails, output the raw content so the user can save it manually.
