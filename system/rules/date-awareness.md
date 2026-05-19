---
name: date-awareness
purpose: Verify the current date at session start; prevent stale dates in file writes.
enabled: disabled by default
---

# Date & Time Awareness

## Purpose

Prevent stale dates from appearing in files, task entries, reviews, and headers by
verifying the actual current date at the start of every conversation.

---

## The Rule

1. **At conversation start** — run `date` (or equivalent) to establish the actual current date.
   Never infer today's date from prior context, memory, or the last file timestamp seen.

2. **When creating or updating files** — verify the date in headers, footers, and `Updated:`
   fields matches the actual current date, not a copy-pasted or assumed date.

3. **When resolving relative terms** — "today", "this week", "this month" must resolve to
   actual calendar dates, not approximations.

4. **Stale header detection** — if a file has an `Updated:` footer that is more than a few
   days old and the file is being modified, flag it and update to the real edit date.

---

## Why This Matters

Files that carry yesterday's date or last week's heading create false audit trails. Task
lists with wrong dates cause missed follow-ups. Reviews with incorrect week labels break
the weekly review pattern.

A 30-second date check at session start prevents all of this.

---

## Implementation

```bash
# Minimal check — run at session start
date +%Y-%m-%d
```

Use `YYYY-MM-DD` as the canonical date format throughout the system.

---

*Module: disabled by default. Enable during `/init-os` or via orchestrator instruction.*
