# Getting Started

From zero to a working Personal OS in under 30 minutes. This guide covers first-time setup
and the daily loop you will run every working day.

---

## Prerequisites

- [Claude Code CLI](https://claude.ai/code) installed and authenticated
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) running
- Python 3.10+

---

## Step 1 — Clone and initialize

```bash
git clone <your-fork-or-this-repo> my-personal-os
cd my-personal-os
```

Run the one-command setup:

```bash
make init
```

`make init` runs `setup.sh`, which:
1. Checks Docker and Python are available.
2. Creates the runtime directories (`daily-ops/tasks/`, `second-brain/inbox/`, etc.).
3. Copies `.env.example` → `.env` (edit this file to set your Postgres and Qdrant ports).
4. Installs the git pre-push privacy hook.
5. Brings up the Docker containers (Postgres + Qdrant).
6. Runs the startup health check.

If `make init` finishes without errors, infra is ready.

---

## Step 2 — Open Claude Code

```bash
claude  # or open the Claude Code desktop app and navigate to this folder
```

Claude Code will read `CLAUDE.md` automatically. You will see the three-domain architecture
loaded: Daily Ops, Second Brain, and Study.

---

## Step 3 — Personalize with `/init-os`

The skeleton ships with `{{PLACEHOLDER}}` tokens throughout its config files. Replace them
all in one session:

```
/init-os
```

`/init-os` will ask you (one question at a time):

- Your name and role (`{{USER_NAME}}`, `{{USER_ROLE}}`)
- Your project/OS name (`{{PROJECT_NAME}}`)
- Your north star goal (`{{NORTH_STAR}}`)
- Your five goal pillars (`{{PILLAR_1}}` through `{{PILLAR_5}}`)
- Which rule modules to enable (elimination, wellbeing-calibrator, spaced-repetition, date-awareness)
- Your first study track name (`{{TRACK_NAME}}`)

It writes the filled values to `CLAUDE.md`, `system/goal-compass.md`, `study/roadmap.template.md`,
and the domain `_index.md` files.

After `/init-os` completes, run:

```bash
make scan    # privacy check — ensure no real data leaked into repo
```

---

## Step 4 — Your first morning briefing

Each morning, open Claude Code in your repo and run:

```
/morning
```

The `morning` skill:
1. Checks the current date.
2. Reads `daily-ops/tasks/today.md` for pending tasks.
3. Shows habits for the day.
4. Checks `daily-ops/reviews/weekly/` for any open items from the last weekly review.
5. If Google Calendar and Gmail MCPs are connected, pulls upcoming events and urgent mail.
6. Ends with a Goal Compass check: which pillar are you pushing today?

---

## Step 5 — Capture during the day

Any time a thought, idea, article, or task comes up:

```
/capture this idea about {{YOUR_TOPIC}}
```

The `capture` skill saves it immediately to `second-brain/inbox/` with a timestamp. No
interruption to your flow — triage it later with the organizer agent.

For tasks specifically:

```
/task add "Write the first draft of X"
/task list
/task done "Write the first draft of X"
/task next        # what should I work on now?
```

---

## Step 6 — Evening review

At the end of the day:

```
/evening
```

The `evening` skill:
1. Shows what was done vs. undone from `daily-ops/tasks/today.md`.
2. Prompts a quick energy/stress check (if the wellbeing-calibrator rule is enabled).
3. Moves incomplete tasks forward or to backlog.
4. Saves an end-of-day note to `daily-ops/reviews/`.

---

## Step 7 — Weekly review

Once a week (Friday or Sunday works well):

```
/weekly-review
```

The `weekly-review` skill:
1. Summarizes wins, misses, and patterns from the week's daily reviews.
2. Checks Goal Compass — which pillars moved, which were neglected.
3. If the elimination rule is enabled, enforces the max-priority cap and moves overflow to
   `daily-ops/tasks/backlog.md`.
4. Produces a written summary saved to `daily-ops/reviews/weekly/`.

---

## Daily Loop — At a Glance

```
Morning      /morning          tasks + habits + Goal Compass check
During day   /capture [text]   quick capture → second-brain/inbox/
             /task [...]       task CRUD
Evening      /evening          review done/undone, energy check, forward tasks
Weekly       /weekly-review    wins, misses, pillars, backlog trim
```

---

## Useful One-Offs

| Command | When to Use |
|---------|------------|
| `/focus study` | Deep work session — load only the Study domain |
| `/focus plan-week` | Weekly planning — ops + study |
| `/focus deep-work` | Focused study — study + brain |
| `/lint` | KB health check — orphans, broken links, stale dates |
| `/backlinks [[ProjectAlpha]]` | Find every file referencing a topic |
| `/reload` | After adding files or agents — re-audit the system |
| `make doctor` | Diagnose infra or config issues |
| `make scan` | Privacy scan before committing or sharing |
| `make test` | Run the test suite (35 hermetic tests) |

---

## Troubleshooting

**Docker containers not starting**
```bash
make doctor     # runs scripts/doctor.sh — checks Docker, .env, Python deps
docker compose ps   # check container status directly
```

**Postgres or Qdrant unreachable**
```bash
bash system/db/startup.sh   # health check with diagnostic output
```

**Privacy scan fails**
```bash
bash scripts/scan-core.sh .   # see which files triggered the scan
# Edit scripts/identifiers.txt to add your personal identifiers
```

**Memory bridge not syncing**
```bash
python system/db/bridge.py status    # check watermark and record counts
python system/db/bridge.py sync      # run manual sync
```

---

## What's Next

- [ARCHITECTURE.md](ARCHITECTURE.md) — deep dive into the agent hierarchy and memory DB
- [CUSTOMIZING.md](CUSTOMIZING.md) — enable rule modules, fill placeholders, tune the system
- [EXTENDING.md](EXTENDING.md) — add new domains, agents, and skills
- [RECOMMENDED-TOOLING.md](RECOMMENDED-TOOLING.md) — optional external tools that integrate well
