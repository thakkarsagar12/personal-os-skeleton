---
name: "Task Management"
description: "Add, list, complete, and navigate tasks in daily-ops/tasks/. Supports subcommands: add, list, done, next, start, blocked, progress, backlog. Use for any task CRUD operation on the daily-ops task files."
---

# Task Management (`/task`)

## What This Skill Does

Manages tasks stored in `daily-ops/tasks/today.md` and `daily-ops/tasks/backlog.md`.
Supports creating, listing, completing, and navigating tasks without leaving the chat.

## Invocation

```
/task <subcommand> [args]
```

---

## Subcommands

### `add`

```
/task add <description> [priority: high|medium|low] [pillar: <name>]
```

Appends a new task to `daily-ops/tasks/today.md`:

```markdown
- [ ] {description}  [priority: {level}]
```

Confirms: `Added: "{description}"`

---

### `list`

```
/task list [filter: open|done|blocked|all]
```

Reads `daily-ops/tasks/today.md` and renders a grouped list.

Default filter: `open`.

Output:

```
## Today's Tasks ({YYYY-MM-DD})

### Open (N)
- [ ] Task A  [high]
- [ ] Task B  [medium]

### Done (N)
- [x] Task C

### Blocked (N)
- [b] Task D — {reason}
```

---

### `done`

```
/task done <task-number or description-fragment>
```

Marks the matching task `[x]` in `daily-ops/tasks/today.md`.

Confirms: `Done: "{description}"`

---

### `next`

```
/task next
```

Returns the single highest-priority open task from `daily-ops/tasks/today.md`.

Output:

```
Next: "{description}"  [priority: high]
```

If nothing is open: `All tasks complete for today.`

---

### `start`

```
/task start <task-number or description-fragment>
```

Marks the matching task `[~]` (in-progress) in `daily-ops/tasks/today.md`.

Confirms: `Started: "{description}"`

---

### `blocked`

```
/task blocked <task-number or description-fragment> [reason]
```

Marks the matching task `[b]` and appends the optional reason inline.

Confirms: `Blocked: "{description}" — {reason}`

---

### `progress`

```
/task progress
```

Shows a one-line count summary:

```
Today: Done N | Open N | In-progress N | Blocked N
```

---

### `backlog`

```
/task backlog [add <description> | list]
```

- `add` → appends to `daily-ops/tasks/backlog.md`
- `list` → reads and displays backlog items (top 10)

---

## Task File Format

`daily-ops/tasks/today.md` uses simple markdown checkboxes:

```markdown
# Tasks — {YYYY-MM-DD}

- [ ] Open task
- [x] Completed task
- [~] In-progress task
- [b] Blocked task — reason
```

Tasks are written in priority order (high → medium → low).

---

## Configuration

| Setting | Location | Notes |
|---------|----------|-------|
| Daily tasks | `daily-ops/tasks/today.md` | Created if absent |
| Backlog | `daily-ops/tasks/backlog.md` | Created if absent |
| Project tasks | `daily-ops/tasks/projects/<name>.md` | One file per project |

---

## Output Rules

- One confirmation line per mutation.
- `list` output grouped and compact — no elaboration.
- `next` returns exactly one item.
- Never ask for confirmation on `add` or `done` — just do it.
