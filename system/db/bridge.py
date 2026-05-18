#!/usr/bin/env python3
"""
Personal OS — claude-mem -> Postgres/Qdrant Bridge

claude-mem (~/.claude-mem/claude-mem.db) is the live write-ahead capture
layer. This bridge mirrors its observations + session_summaries into the
Personal OS system-of-record (Postgres) and semantic layer (Qdrant),
rebuilding conversations / segments / summaries / topics / decisions.

Idempotent. Safe to re-run. Designed for nightly cron.

Usage:
    python bridge.py sync               # incremental (since watermark)
    python bridge.py sync --backfill    # from epoch 0 (first run / gap fill)
    python bridge.py sync --no-embed    # structural only, skip Qdrant vectors
    python bridge.py status             # show watermark + counts
    python bridge.py sync --dry-run     # report what would change, no writes

Source filter: only claude-mem projects in PROJECTS (this repo's sessions).
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memory as mem  # reuse get_conn / embed / _upsert_vector / COLLECTIONS

CLAUDE_MEM_DB = os.path.expanduser(
    os.getenv("CLAUDE_MEM_DB", "~/.claude-mem/claude-mem.db")
)
PROJECTS = ("PROJECT_LABEL", "PROJECT_LABEL")  # claude-mem project labels for this repo
SOURCE = "claude-mem"

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INCOGNITO_LOG = os.path.join(_REPO, "system", ".incognito-windows.log")


def load_incognito_windows():
    """Return [(start_ms, end_ms)] from the append-only incognito log.
    Open windows (no END) extend to 'now'. Honors /incognito so private
    sessions never reach the permanent Postgres/Qdrant store, even though
    claude-mem still keeps its own local copy."""
    wins = []
    if not os.path.exists(INCOGNITO_LOG):
        return wins
    now_ms = datetime.now(timezone.utc).timestamp() * 1000
    with open(INCOGNITO_LOG) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            s = parts[0].strip()
            e = parts[1].strip() if len(parts) > 1 else ""
            try:
                s_ms = datetime.fromisoformat(
                    s.replace("Z", "+00:00")).timestamp() * 1000
                e_ms = (datetime.fromisoformat(e.replace("Z", "+00:00"))
                        .timestamp() * 1000) if e else now_ms
                wins.append((s_ms, e_ms))
            except Exception:
                continue
    return wins


def _in_incognito(epoch_ms, windows):
    return any(s <= epoch_ms <= e for s, e in windows)

# claude-mem type -> Personal OS segments.type (constrained enum:
# discussion|decision|plan-change|insight|action|blocker)
TYPE_MAP = {
    "decision": "decision",
    "discovery": "insight",
    "feature": "plan-change",
    "change": "plan-change",
    "refactor": "plan-change",
    "bugfix": "action",
    "session": "discussion",
    "security_alert": "blocker",
    "security_note": "blocker",
}


def map_seg_type(cm_type):
    return TYPE_MAP.get((cm_type or "").strip().lstrip("🎯🔴🟣🔄✅🔵⚖️🚨🔐").strip(),
                        "discussion")


# ── schema (bridge-owned bookkeeping) ───────────────────────────────

def ensure_bridge_schema(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bridge_state (
                source        TEXT PRIMARY KEY,
                last_epoch    DOUBLE PRECISION NOT NULL DEFAULT 0,
                last_run_at   TIMESTAMPTZ,
                total_synced  INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS bridge_obs_map (
                cm_rowid    INTEGER PRIMARY KEY,
                kind        TEXT NOT NULL,           -- 'segment' | 'decision'
                target_id   INTEGER NOT NULL,
                synced_at   TIMESTAMPTZ DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS bridge_session_map (
                cm_session_id TEXT PRIMARY KEY,
                conversation_id INTEGER NOT NULL,
                summary_id    INTEGER,
                synced_at     TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        conn.commit()


def get_watermark(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT last_epoch, total_synced FROM bridge_state WHERE source=%s",
                    (SOURCE,))
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO bridge_state (source) VALUES (%s)", (SOURCE,))
            conn.commit()
            return 0.0, 0
        return float(row[0]), int(row[1])


def set_watermark(conn, last_epoch, added):
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE bridge_state
               SET last_epoch=%s, last_run_at=NOW(), total_synced=total_synced+%s
               WHERE source=%s""",
            (last_epoch, added, SOURCE),
        )
        conn.commit()


# ── claude-mem readers ──────────────────────────────────────────────

def cm_connect():
    if not os.path.exists(CLAUDE_MEM_DB):
        print(json.dumps({"error": f"claude-mem db not found: {CLAUDE_MEM_DB}"}))
        sys.exit(2)
    return sqlite3.connect(f"file:{CLAUDE_MEM_DB}?mode=ro", uri=True)


def fetch_new_observations(cm, since_epoch):
    placeholders = ",".join("?" * len(PROJECTS))
    cur = cm.cursor()
    cur.execute(f"""
        SELECT id, memory_session_id, project, text, type, title, subtitle,
               facts, narrative, concepts, files_read, files_modified,
               prompt_number, created_at, created_at_epoch
        FROM observations
        WHERE project IN ({placeholders}) AND created_at_epoch > ?
        ORDER BY created_at_epoch ASC
    """, (*PROJECTS, since_epoch))
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def fetch_summaries_for(cm, session_ids):
    if not session_ids:
        return {}
    ph = ",".join("?" * len(session_ids))
    cur = cm.cursor()
    cur.execute(f"""
        SELECT memory_session_id, request, investigated, learned, completed,
               next_steps, notes, created_at, created_at_epoch
        FROM session_summaries
        WHERE memory_session_id IN ({ph})
        ORDER BY created_at_epoch ASC
    """, tuple(session_ids))
    cols = [d[0] for d in cur.description]
    out = {}
    for r in cur.fetchall():
        d = dict(zip(cols, r))
        out[d["memory_session_id"]] = d  # last (newest) wins
    return out


# ── mapping helpers ─────────────────────────────────────────────────

def iso(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def seg_content(o):
    parts = []
    if o.get("title"):
        parts.append(o["title"])
    if o.get("subtitle"):
        parts.append(o["subtitle"])
    body = o.get("narrative") or o.get("text") or ""
    if body:
        parts.append(body)
    if o.get("facts"):
        parts.append(f"Facts: {o['facts']}")
    return "\n".join(parts).strip() or (o.get("type") or "observation")


def concepts_list(o):
    raw = (o.get("concepts") or "").strip()
    if not raw:
        return []
    try:
        v = json.loads(raw)
        if isinstance(v, list):
            return [str(c).strip() for c in v if str(c).strip()][:8]
        raw = str(v)
    except Exception:
        pass
    for sep in ("|", ",", ";"):
        if sep in raw:
            return [c.strip() for c in raw.split(sep) if c.strip()][:8]
    return [raw][:8]


def upsert_conversation(conn, cm_session_id, title, started, ended):
    sid = f"cm-{cm_session_id}"[:64]
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM conversations WHERE session_id=%s", (sid,))
        row = cur.fetchone()
        if row:
            cur.execute(
                """UPDATE conversations
                   SET title=%s, ended_at=%s, status='completed'
                   WHERE id=%s""",
                (title[:200], ended, row[0]),
            )
            return row[0]
        cur.execute(
            """INSERT INTO conversations
               (session_id, title, started_at, ended_at, domains, pillars, status)
               VALUES (%s,%s,%s,%s,'{}','{}','completed') RETURNING id""",
            (sid, title[:200], started, ended),
        )
        return cur.fetchone()[0]


def already_mapped(conn, rowids):
    if not rowids:
        return set()
    with conn.cursor() as cur:
        cur.execute("SELECT cm_rowid FROM bridge_obs_map WHERE cm_rowid = ANY(%s)",
                    (list(rowids),))
        return {r[0] for r in cur.fetchall()}


def link_topics(conn, conv_id, concepts):
    for name in concepts:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM topics WHERE name=%s", (name,))
            t = cur.fetchone()
            if not t:
                cur.execute(
                    """INSERT INTO topics (name, status, first_discussed, last_discussed)
                       VALUES (%s,'active',NOW(),NOW()) RETURNING id""", (name,))
                tid = cur.fetchone()[0]
            else:
                tid = t[0]
                cur.execute("UPDATE topics SET last_discussed=NOW() WHERE id=%s", (tid,))
            cur.execute(
                """INSERT INTO conversation_topics (conversation_id, topic_id, relevance)
                   VALUES (%s,%s,'related') ON CONFLICT DO NOTHING""",
                (conv_id, tid),
            )


# ── core sync ───────────────────────────────────────────────────────

def sync(backfill=False, do_embed=True, dry_run=False):
    conn = mem.get_conn()
    ensure_bridge_schema(conn)
    last_epoch, _ = get_watermark(conn)
    since = 0.0 if backfill else last_epoch

    cm = cm_connect()
    obs = fetch_new_observations(cm, since)
    if not obs:
        cm.close()
        print(json.dumps({"status": "up-to-date", "since_epoch": since,
                          "new_observations": 0}))
        return

    # Honor /incognito — drop observations captured during private windows
    # so they never reach the permanent Postgres/Qdrant store (claude-mem
    # keeps its own local copy; the searchable store does not).
    max_seen = max(o["created_at_epoch"] for o in obs)  # advance past private too
    incog_wins = load_incognito_windows()
    incognito_skipped = 0
    if incog_wins:
        kept = []
        for o in obs:
            if _in_incognito(o["created_at_epoch"], incog_wins):
                incognito_skipped += 1
            else:
                kept.append(o)
        obs = kept
    if not obs:
        # everything in this batch was private — record nothing, but
        # advance the watermark so private obs aren't re-scanned forever.
        set_watermark(conn, max_seen, 0)
        conn.close()
        cm.close()
        print(json.dumps({"status": "all-incognito", "since_epoch": since,
                          "incognito_skipped": incognito_skipped}))
        return

    # group by session
    sessions = {}
    for o in obs:
        sessions.setdefault(o["memory_session_id"], []).append(o)
    summaries = fetch_summaries_for(cm, list(sessions.keys()))
    cm.close()

    new_rowids = {o["id"] for o in obs}
    skip = already_mapped(conn, new_rowids)

    stats = {"conversations": 0, "segments": 0, "summaries": 0,
             "decisions": 0, "skipped": len(skip),
             "incognito_skipped": incognito_skipped, "embedded": 0}
    max_epoch = since

    for sid, items in sessions.items():
        items.sort(key=lambda x: (x.get("prompt_number") or 0, x["created_at_epoch"]))
        started = iso(items[0]["created_at"])
        ended = iso(items[-1]["created_at"])
        summ = summaries.get(sid)
        title = (summ["request"] if summ and summ.get("request")
                 else items[0].get("title") or f"claude-mem {started.date()}")

        if dry_run:
            stats["conversations"] += 1
            stats["segments"] += sum(1 for o in items if o["id"] not in skip)
            if summ:
                stats["summaries"] += 1
            max_epoch = max(max_epoch, max(o["created_at_epoch"] for o in items))
            continue

        conv_id = upsert_conversation(conn, sid, title, started, ended)
        stats["conversations"] += 1
        all_concepts = set()

        for o in items:
            max_epoch = max(max_epoch, o["created_at_epoch"])
            if o["id"] in skip:
                continue
            content = seg_content(o)
            raw_type = (o.get("type") or "discussion").strip()
            seg_type = map_seg_type(raw_type)
            concepts = concepts_list(o)
            all_concepts.update(concepts)
            tags = concepts + [f"cm:{raw_type}"]
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO segments
                       (conversation_id, type, content, tags, sequence, created_at)
                       VALUES (%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (conv_id, seg_type, content, tags,
                     o.get("prompt_number") or 0, iso(o["created_at"])),
                )
                seg_id = cur.fetchone()[0]
                cur.execute(
                    """INSERT INTO bridge_obs_map (cm_rowid, kind, target_id)
                       VALUES (%s,'segment',%s)
                       ON CONFLICT (cm_rowid) DO NOTHING""",
                    (o["id"], seg_id),
                )
            stats["segments"] += 1

            if seg_type == "decision":
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO decisions
                           (conversation_id, decision, context, decided_at, status)
                           VALUES (%s,%s,%s,%s,'active') RETURNING id""",
                        (conv_id, (o.get("title") or content)[:500],
                         content, iso(o["created_at"])),
                    )
                stats["decisions"] += 1

            if do_embed:
                try:
                    mem._upsert_vector("segments", seg_id, mem.embed(content),
                                       {"conversation_id": conv_id,
                                        "session_id": f"cm-{sid}",
                                        "type": raw_type, "source": SOURCE})
                    stats["embedded"] += 1
                except Exception as e:
                    print(f"[warn] embed failed seg {seg_id}: {e}", file=sys.stderr)

        if all_concepts:
            link_topics(conn, conv_id, sorted(all_concepts))

        if summ:
            blocks = []
            for k in ("investigated", "learned", "completed"):
                if summ.get(k):
                    blocks.append(f"**{k.title()}:** {summ[k]}")
            summary_text = "\n\n".join(blocks) or (summ.get("notes") or title)
            outcomes = [s.strip() for s in (summ.get("next_steps") or "").split("\n")
                        if s.strip()][:10]
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT summary_id FROM bridge_session_map WHERE cm_session_id=%s",
                    (sid,))
                existing = cur.fetchone()
                if existing and existing[0]:
                    cur.execute("UPDATE summaries SET summary=%s, key_outcomes=%s WHERE id=%s",
                                (summary_text, outcomes, existing[0]))
                    sum_id = existing[0]
                else:
                    cur.execute(
                        """INSERT INTO summaries (conversation_id, summary, key_outcomes)
                           VALUES (%s,%s,%s) RETURNING id""",
                        (conv_id, summary_text, outcomes))
                    sum_id = cur.fetchone()[0]
                cur.execute(
                    """INSERT INTO bridge_session_map (cm_session_id, conversation_id, summary_id)
                       VALUES (%s,%s,%s)
                       ON CONFLICT (cm_session_id)
                       DO UPDATE SET conversation_id=EXCLUDED.conversation_id,
                                     summary_id=EXCLUDED.summary_id""",
                    (sid, conv_id, sum_id))
            stats["summaries"] += 1
            if do_embed:
                try:
                    mem._upsert_vector("summaries", sum_id, mem.embed(summary_text),
                                       {"conversation_id": conv_id, "session_id": f"cm-{sid}",
                                        "source": SOURCE})
                except Exception as e:
                    print(f"[warn] embed summary {sum_id}: {e}", file=sys.stderr)

        conn.commit()

    # advance past incognito-only trailing obs too (max_seen >= max_epoch)
    final_epoch = max(max_epoch, max_seen)
    if not dry_run:
        set_watermark(conn, final_epoch, stats["segments"])
    conn.close()
    print(json.dumps({"status": "dry-run" if dry_run else "synced",
                       "backfill": backfill, "from_epoch": since,
                       "to_epoch": final_epoch, **stats}))


def reembed(limit=None):
    """Push Qdrant vectors for all bridged (cm-) segments + summaries.
    Idempotent: Qdrant upsert by point id. Use after a --no-embed backfill
    or to rebuild the semantic index."""
    conn = mem.get_conn()
    n_seg = n_sum = 0
    with conn.cursor() as cur:
        q = """SELECT s.id, s.content, s.conversation_id, s.type, c.session_id
               FROM segments s JOIN conversations c ON c.id=s.conversation_id
               WHERE c.session_id LIKE 'cm-%' ORDER BY s.id"""
        if limit:
            q += f" LIMIT {int(limit)}"
        cur.execute(q)
        rows = cur.fetchall()
    for sid_, content, conv_id, stype, sess in rows:
        try:
            mem._upsert_vector("segments", sid_, mem.embed(content),
                               {"conversation_id": conv_id, "session_id": sess,
                                "type": stype, "source": SOURCE})
            n_seg += 1
        except Exception as e:
            print(f"[warn] embed seg {sid_}: {e}", file=sys.stderr)
    with conn.cursor() as cur:
        cur.execute("""SELECT su.id, su.summary, su.conversation_id, c.session_id
                       FROM summaries su JOIN conversations c ON c.id=su.conversation_id
                       WHERE c.session_id LIKE 'cm-%'""")
        srows = cur.fetchall()
    for su_id, summ, conv_id, sess in srows:
        try:
            mem._upsert_vector("summaries", su_id, mem.embed(summ or ""),
                               {"conversation_id": conv_id, "session_id": sess,
                                "source": SOURCE})
            n_sum += 1
        except Exception as e:
            print(f"[warn] embed summary {su_id}: {e}", file=sys.stderr)
    conn.close()
    print(json.dumps({"status": "reembedded", "segments": n_seg,
                      "summaries": n_sum}))


def status():
    conn = mem.get_conn()
    ensure_bridge_schema(conn)
    le, total = get_watermark(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM bridge_obs_map")
        mapped = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM conversations WHERE session_id LIKE 'cm-%'")
        convs = cur.fetchone()[0]
    conn.close()
    cm = cm_connect()
    c = cm.cursor()
    ph = ",".join("?" * len(PROJECTS))
    c.execute(f"SELECT count(*) FROM observations WHERE project IN ({ph})", PROJECTS)
    src = c.fetchone()[0]
    cm.close()
    print(json.dumps({"source": SOURCE, "last_epoch": le, "total_synced": total,
                      "obs_mapped": mapped, "bridged_conversations": convs,
                      "claude_mem_source_obs": src,
                      "human_last_run": datetime.fromtimestamp(le/1000).isoformat()
                      if le else None}))


def main():
    p = argparse.ArgumentParser(description="claude-mem -> Postgres/Qdrant bridge")
    sub = p.add_subparsers(dest="command")
    s = sub.add_parser("sync")
    s.add_argument("--backfill", action="store_true")
    s.add_argument("--no-embed", action="store_true")
    s.add_argument("--dry-run", action="store_true")
    sub.add_parser("status")
    re = sub.add_parser("reembed")
    re.add_argument("--limit", type=int, default=None)
    args = p.parse_args()
    if args.command == "status":
        status()
    elif args.command == "reembed":
        reembed(limit=args.limit)
    elif args.command == "sync":
        sync(backfill=args.backfill, do_embed=not args.no_embed,
             dry_run=args.dry_run)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
