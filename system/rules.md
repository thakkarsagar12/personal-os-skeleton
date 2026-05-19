---
name: system-rules
purpose: Rule framework overview + opt-in module index. Full rule bodies live in system/rules/*.md.
---

# Operating Rule Framework

This file describes how rules work in Personal OS and indexes the available opt-in modules.

Rule bodies are NOT defined here — they live in `system/rules/`. This keeps CLAUDE.md and
core system files lean while still making each rule auditable and version-controlled.

---

## How Rules Work

Rules are persistent behaviors that run across every conversation, regardless of which domain
or focus mode is active. They are applied by the master-orchestrator and domain leads.

**Two layers:**

1. **Core behaviors** — Baked into CLAUDE.md (always active, non-configurable here):
   response formatting, communication style, one-question-at-a-time protocol.

2. **Opt-in modules** — Defined in `system/rules/*.md`. Each module is **disabled by default**
   and must be explicitly enabled during `/init-os` setup or via a direct instruction.

---

## Enabling Modules

During initial setup (`/init-os`), you will be prompted to enable each module.
To enable or disable a module after setup, edit the **Enabled** column in the table below
from `disabled by default` to `enabled`, or instruct the orchestrator directly.

---

## Module Index

| Module File | What It Does | Enabled |
|-------------|-------------|---------|
| `system/rules/elimination.md` | Caps weekly active priorities; overflows to backlog | disabled by default |
| `system/rules/wellbeing-calibrator.md` | Energy/stress self-rating adapts task load | disabled by default |
| `system/rules/spaced-repetition.md` | Spaced repetition schedule and revision modes | disabled by default |
| `system/rules/date-awareness.md` | Verifies current date at session start; prevents stale dates | disabled by default |

---

## Adding Custom Rules

To add a rule beyond these four modules:

1. Create `system/rules/your-rule-name.md` following the pattern in the existing modules.
2. Add a row to the Module Index table above.
3. Enable it via the table or by instructing the orchestrator.

Rules should be self-contained — each file should describe exactly what to do and when,
without depending on personal data that isn't defined in a placeholder.

---

*Template file — personalize after running `/init-os`.*
