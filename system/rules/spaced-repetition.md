---
name: spaced-repetition
purpose: Generic spaced repetition schedule and revision modes for study topics.
enabled: disabled by default
---

# Spaced Repetition

## Purpose

Ensure studied topics are revisited at increasing intervals so they move from short-term
recall into durable long-term memory.

---

## Schedule

Standard interval ladder (days since last review):

| Stage | Interval |
|-------|----------|
| 1 | 1 day |
| 2 | 3 days |
| 3 | 7 days |
| 4 | 14 days |
| 5 | 30 days |
| 6 | 90 days |

When a topic is reviewed successfully it advances one stage. When a topic is recalled
incorrectly or the review is skipped repeatedly it moves back one stage.

---

## Active Queue Cap

Keep at most **N topics** in the active revision queue at once (set N during `/init-os`, default 8).

- When a new topic would exceed the cap, move the oldest / lowest-priority active topic to
  the dormant list.
- Dormant topics are not surfaced until manually reactivated.
- Reactivation is explicit — the user or orchestrator must request it.

This cap is the primary load governor. It prevents review debt from accumulating.

---

## Tracking

Store the queue in `system/spaced-repetition.md` (create if absent). Minimum columns:

```
| Topic | Track | Stage | Last Reviewed | Next Due | Status |
|-------|-------|-------|--------------|----------|--------|
```

Status values: `active` | `dormant`.

Auto-add a new row whenever a study topic is completed. Update stage and dates after each review.

---

## Revision Modes

Use the mode that fits the session. Listed from most effective to least:

1. **Teach-back** — explain the topic aloud or in writing as if teaching someone else.
   Best for consolidation. Use for the majority of reviews.

2. **Discussion** — open-ended conversation about the topic. Good when teach-back feels
   too formal or energy is low. Counts as a valid review touch.

3. **Flashcard Q&A** — direct question-and-answer drill. Use for cold topics or quick
   stage-1 checks when time is short.

---

## Q&A Card Repository

Every study Q&A session generates cards stored at `study/{track}/cards/{topic}.md`.

Card format:
```
## Card N
**Q:** The question
**A:** The answer
**Gap:** Any misconception identified (if applicable)
**Difficulty:** easy / medium / hard
```

During a revision session, use existing cards — do not generate new questions.
After a review, update difficulty (correct → downgrade one level; incorrect → upgrade one level).

---

## Escalation

If a topic has been skipped 2+ consecutive review dates, surface a brief prompt:
"[Topic] is overdue. 5-minute review now?"

Do not guilt or penalize. A missed review is a missed review — the schedule adjusts forward,
not backward.

---

## Triggering a Session

Trigger a revision session against the active queue when ready.

---

*Module: disabled by default. Enable during `/init-os` or via orchestrator instruction.*
