#!/usr/bin/env python3
"""
Personal OS — Conversation Memory CLI
Two-layer memory: Postgres (relational) + Qdrant (vector search)

Usage:
    python memory.py start "Title" --domains study ops --pillars skill-depth
    python memory.py segment <session_id> "content" --type discussion --tags "ai" "transformers"
    python memory.py end <session_id> --summary "What we discussed" --outcomes "outcome1" "outcome2"
    python memory.py topic create "topic-name" --domain study --pillar skill-depth --description "..."
    python memory.py topic link <session_id> <topic_name> --relevance primary
    python memory.py decide <session_id> "decision text" --topic "topic-name" --context "why" --from "Plan A" --to "Plan B"
    python memory.py pointer <session_id> "insight content" --type insight --topic "topic-name" --domain study
    python memory.py search "what was the database decision"
    python memory.py search-segments "transformer architecture" --type discussion
    python memory.py search-pointers "database architecture"
    python memory.py timeline "topic-name"
    python memory.py decisions [--topic "topic-name"]
    python memory.py pointers [--topic "topic-name"] [--type insight]
    python memory.py merge-pointer <pointer_id> <into_pointer_id>
    python memory.py recent [--limit 10]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from uuid import uuid4

import psycopg2
from psycopg2.extras import RealDictCursor

# Lazy-load heavy imports
_model = None
_qdrant = None

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_HTTP_PORT", "$QDRANT_PORT"))

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PENDING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pending")
PROCESSED_DIR = os.path.join(PENDING_DIR, "processed")

COLLECTIONS = {
    "segments": "personal_os_segments",
    "summaries": "personal_os_summaries",
    "pointers": "personal_os_pointers",
}

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_qdrant():
    global _qdrant
    if _qdrant is None:
        from qdrant_client import QdrantClient
        _qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        _ensure_collections()
    return _qdrant

def _ensure_collections():
    from qdrant_client.models import Distance, VectorParams
    client = _qdrant
    existing = {c.name for c in client.get_collections().collections}
    for name in COLLECTIONS.values():
        if name not in existing:
            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

def embed(text: str) -> list:
    return get_model().encode(text).tolist()

def get_conn():
    return psycopg2.connect(
        dbname=os.getenv("PGDATABASE", "personal_os"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "postgres"),
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "$POSTGRES_PORT"),
    )

# ── Qdrant helpers ─────────────────────────────────────────

def _upsert_vector(collection: str, point_id: int, vector: list, payload: dict):
    from qdrant_client.models import PointStruct
    get_qdrant().upsert(
        collection_name=COLLECTIONS[collection],
        points=[PointStruct(id=point_id, vector=vector, payload=payload)],
    )

def _search_vectors(collection: str, query_vector: list, limit: int = 10, filters: dict = None):
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    q_filter = None
    if filters:
        conditions = [FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filters.items()]
        q_filter = Filter(must=conditions)
    return get_qdrant().query_points(
        collection_name=COLLECTIONS[collection],
        query=query_vector,
        limit=limit,
        query_filter=q_filter,
    ).points

# ── Conversation lifecycle ──────────────────────────────────

def start_conversation(title, domains=None, pillars=None, focus_mode=None):
    if TEST_TITLE_RE.match(title or "") and os.getenv("POS_ALLOW_TEST") != "1":
        print(json.dumps({"error": "test-like title rejected — set "
                          "POS_ALLOW_TEST=1 to override", "title": title}))
        return None
    session_id = str(uuid4())[:12]
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO conversations (session_id, title, domains, pillars, focus_mode)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id, session_id""",
                (session_id, title, domains or [], pillars or [], focus_mode),
            )
            row = cur.fetchone()
            conn.commit()
    print(json.dumps({"id": row[0], "session_id": row[1]}))
    return row[1]

def end_conversation(session_id, summary=None, outcomes=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE conversations SET status = 'completed', ended_at = NOW()
                   WHERE session_id = %s RETURNING id""",
                (session_id,),
            )
            conv_id = cur.fetchone()[0]

            if summary:
                cur.execute(
                    """INSERT INTO summaries (conversation_id, summary, key_outcomes)
                       VALUES (%s, %s, %s) RETURNING id""",
                    (conv_id, summary, outcomes or []),
                )
                sum_id = cur.fetchone()[0]
                vec = embed(summary)
                _upsert_vector("summaries", sum_id, vec, {
                    "conversation_id": conv_id,
                    "session_id": session_id,
                })
            conn.commit()
    print(json.dumps({"status": "completed", "session_id": session_id}))

# ── Segments ────────────────────────────────────────────────

def add_segment(session_id, content, type_="discussion", tags=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT COALESCE(MAX(s.sequence), 0) + 1
                   FROM segments s
                   JOIN conversations c ON c.id = s.conversation_id
                   WHERE c.session_id = %s""",
                (session_id,),
            )
            seq = cur.fetchone()[0]

            cur.execute(
                """INSERT INTO segments (conversation_id, type, content, tags, sequence)
                   SELECT c.id, %s, %s, %s, %s
                   FROM conversations c WHERE c.session_id = %s
                   RETURNING id, conversation_id""",
                (type_, content, tags or [], seq, session_id),
            )
            row = cur.fetchone()
            seg_id, conv_id = row[0], row[1]
            conn.commit()

    vec = embed(content)
    _upsert_vector("segments", seg_id, vec, {
        "conversation_id": conv_id,
        "session_id": session_id,
        "type": type_,
        "tags": tags or [],
    })
    print(json.dumps({"segment_id": seg_id, "sequence": seq}))

def search_segments(query, type_=None, limit=10):
    vec = embed(query)
    filters = {"type": type_} if type_ else None
    results = _search_vectors("segments", vec, limit=limit, filters=filters)

    if not results:
        print(json.dumps([]))
        return

    seg_ids = [r.id for r in results]
    scores = {r.id: r.score for r in results}

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT seg.id, seg.type, seg.content, seg.tags, seg.sequence,
                          c.session_id, c.title, c.started_at::text
                   FROM segments seg
                   JOIN conversations c ON c.id = seg.conversation_id
                   WHERE seg.id = ANY(%s)""",
                (seg_ids,),
            )
            rows = cur.fetchall()

    for row in rows:
        row["similarity"] = scores.get(row["id"], 0)
    rows.sort(key=lambda r: r["similarity"], reverse=True)
    print(json.dumps(rows, indent=2, default=str))

# ── Topics ──────────────────────────────────────────────────

def create_topic(name, domain=None, pillar=None, description=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO topics (name, domain, pillar, description)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (name) DO UPDATE SET last_discussed = NOW()
                   RETURNING id""",
                (name, domain, pillar, description),
            )
            topic_id = cur.fetchone()[0]
            conn.commit()
    print(json.dumps({"topic_id": topic_id, "name": name}))

def link_topic(session_id, topic_name, relevance="primary"):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO conversation_topics (conversation_id, topic_id, relevance)
                   SELECT c.id, t.id, %s
                   FROM conversations c, topics t
                   WHERE c.session_id = %s AND t.name = %s
                   ON CONFLICT DO NOTHING
                   RETURNING conversation_id""",
                (relevance, session_id, topic_name),
            )
            conn.commit()
    print(json.dumps({"linked": True, "session_id": session_id, "topic": topic_name}))

# ── Decisions ───────────────────────────────────────────────

def add_decision(session_id, decision, topic_name=None, context=None, prev=None, new=None):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            topic_id = None
            if topic_name:
                cur.execute("SELECT id FROM topics WHERE name = %s", (topic_name,))
                row = cur.fetchone()
                if row:
                    topic_id = row["id"]

            if topic_id:
                cur.execute(
                    """UPDATE decisions SET status = 'superseded'
                       WHERE topic_id = %s AND status = 'active'
                       RETURNING id""",
                    (topic_id,),
                )
                superseded = cur.fetchone()
            else:
                superseded = None

            cur.execute(
                """INSERT INTO decisions (conversation_id, topic_id, decision, context, previous_state, new_state)
                   SELECT c.id, %s, %s, %s, %s, %s
                   FROM conversations c WHERE c.session_id = %s
                   RETURNING id""",
                (topic_id, decision, context, prev, new, session_id),
            )
            dec_id = cur.fetchone()["id"]

            if superseded:
                cur.execute(
                    "UPDATE decisions SET superseded_by = %s WHERE id = %s",
                    (dec_id, superseded["id"]),
                )
            conn.commit()
    print(json.dumps({"decision_id": dec_id, "superseded": superseded["id"] if superseded else None}))

# ── Pointers ────────────────────────────────────────────────

def add_pointer(session_id, content, type_="insight", topic_name=None, domain=None, pillar=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            topic_id = None
            if topic_name:
                cur.execute("SELECT id FROM topics WHERE name = %s", (topic_name,))
                row = cur.fetchone()
                if row:
                    topic_id = row[0]

            cur.execute(
                """INSERT INTO pointers (conversation_id, topic_id, content, type, domain, pillar)
                   SELECT c.id, %s, %s, %s, %s, %s
                   FROM conversations c WHERE c.session_id = %s
                   RETURNING id, conversation_id""",
                (topic_id, content, type_, domain, pillar, session_id),
            )
            row = cur.fetchone()
            ptr_id, conv_id = row[0], row[1]
            conn.commit()

    vec = embed(content)
    _upsert_vector("pointers", ptr_id, vec, {
        "conversation_id": conv_id,
        "session_id": session_id,
        "type": type_,
        "domain": domain or "",
        "pillar": pillar or "",
    })
    print(json.dumps({"pointer_id": ptr_id}))

def merge_pointer(pointer_id, into_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE pointers SET status = 'merged', merged_into = %s WHERE id = %s",
                (into_id, pointer_id),
            )
            conn.commit()
    print(json.dumps({"merged": pointer_id, "into": into_id}))

# ── Search ──────────────────────────────────────────────────

def search_summaries(query, limit=5):
    vec = embed(query)
    results = _search_vectors("summaries", vec, limit=limit)

    if not results:
        print(json.dumps([]))
        return

    sum_ids = [r.id for r in results]
    scores = {r.id: r.score for r in results}

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT c.session_id, c.title, c.started_at::text, c.domains, c.pillars,
                          s.id AS summary_id, s.summary, s.key_outcomes
                   FROM summaries s
                   JOIN conversations c ON c.id = s.conversation_id
                   WHERE s.id = ANY(%s)""",
                (sum_ids,),
            )
            rows = cur.fetchall()

    for row in rows:
        row["similarity"] = scores.get(row["summary_id"], 0)
    rows.sort(key=lambda r: r["similarity"], reverse=True)
    print(json.dumps(rows, indent=2, default=str))

def search_pointers(query, limit=10):
    vec = embed(query)
    results = _search_vectors("pointers", vec, limit=limit)

    if not results:
        print(json.dumps([]))
        return

    ptr_ids = [r.id for r in results]
    scores = {r.id: r.score for r in results}

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT p.id, p.content, p.type, p.domain, p.pillar, p.status,
                          t.name AS topic, c.title AS conversation, c.started_at::text
                   FROM pointers p
                   LEFT JOIN topics t ON t.id = p.topic_id
                   LEFT JOIN conversations c ON c.id = p.conversation_id
                   WHERE p.id = ANY(%s) AND p.status = 'active'""",
                (ptr_ids,),
            )
            rows = cur.fetchall()

    for row in rows:
        row["similarity"] = scores.get(row["id"], 0)
    rows.sort(key=lambda r: r["similarity"], reverse=True)
    print(json.dumps(rows, indent=2, default=str))

def get_timeline(topic_name):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM topic_timeline WHERE topic = %s", (topic_name,))
            rows = cur.fetchall()
    print(json.dumps(rows, indent=2, default=str))

def list_decisions(topic_name=None):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if topic_name:
                cur.execute("SELECT * FROM active_decisions WHERE topic = %s", (topic_name,))
            else:
                cur.execute("SELECT * FROM active_decisions")
            rows = cur.fetchall()
    print(json.dumps(rows, indent=2, default=str))

def list_pointers(topic_name=None, type_=None):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = "SELECT * FROM available_pointers WHERE 1=1"
            params = []
            if topic_name:
                query += " AND topic = %s"
                params.append(topic_name)
            if type_:
                query += " AND type = %s"
                params.append(type_)
            cur.execute(query, params)
            rows = cur.fetchall()
    print(json.dumps(rows, indent=2, default=str))

def recent_conversations(limit=10):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT c.session_id, c.title, c.started_at::text, c.ended_at::text,
                          c.domains, c.pillars, c.status, s.summary
                   FROM conversations c
                   LEFT JOIN summaries s ON s.conversation_id = c.id
                   ORDER BY c.started_at DESC
                   LIMIT %s""",
                (limit,),
            )
            rows = cur.fetchall()
    print(json.dumps(rows, indent=2, default=str))

# ── Markdown Fallback ──────────────────────────────────────

def save_to_markdown(session_id, title, domains=None, pillars=None):
    """Create a pending markdown file when DB is unavailable."""
    os.makedirs(PENDING_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d-%H%M")
    filename = f"{ts}-{session_id}.md"
    filepath = os.path.join(PENDING_DIR, filename)
    content = f"""---
session_id: {session_id}
title: {title}
domains: {json.dumps(domains or [])}
pillars: {json.dumps(pillars or [])}
started_at: {datetime.now(timezone.utc).isoformat()}
status: pending
---

# {title}

## Segments

"""
    with open(filepath, "w") as f:
        f.write(content)
    print(json.dumps({"session_id": session_id, "file": filepath, "mode": "markdown-fallback"}))
    return filepath


def append_segment_md(session_id, content, type_="discussion", tags=None):
    """Append a segment to a pending markdown file."""
    import glob
    pattern = os.path.join(PENDING_DIR, f"*-{session_id}.md")
    files = glob.glob(pattern)
    if not files:
        print(json.dumps({"error": f"No pending file for session {session_id}"}))
        return
    filepath = files[0]
    ts = datetime.now().strftime("%H:%M")
    entry = f"### [{ts}] {type_}\n**Tags:** {', '.join(tags or [])}\n\n{content}\n\n"
    with open(filepath, "a") as f:
        f.write(entry)
    print(json.dumps({"appended": True, "file": filepath}))


def end_session_md(session_id, summary=None, outcomes=None):
    """Close a pending markdown session."""
    import glob
    pattern = os.path.join(PENDING_DIR, f"*-{session_id}.md")
    files = glob.glob(pattern)
    if not files:
        print(json.dumps({"error": f"No pending file for session {session_id}"}))
        return
    filepath = files[0]
    entry = f"\n---\n\n## Summary\n\n{summary or 'No summary provided.'}\n\n"
    if outcomes:
        entry += "## Outcomes\n\n"
        for o in outcomes:
            entry += f"- {o}\n"
    entry += f"\n---\n*Ended: {datetime.now(timezone.utc).isoformat()}*\n*Status: pending-sync*\n"
    with open(filepath, "a") as f:
        f.write(entry)

    # Update frontmatter status
    with open(filepath, "r") as f:
        text = f.read()
    text = text.replace("status: pending", "status: pending-sync", 1)
    with open(filepath, "w") as f:
        f.write(text)
    print(json.dumps({"closed": True, "file": filepath, "mode": "pending-sync"}))


def sync_pending():
    """Process all pending markdown files into the database."""
    import glob
    import re
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    pattern = os.path.join(PENDING_DIR, "*.md")
    files = sorted(glob.glob(pattern))

    if not files:
        print(json.dumps({"synced": 0, "message": "No pending files"}))
        return

    synced = 0
    errors = 0

    for filepath in files:
        try:
            with open(filepath, "r") as f:
                text = f.read()

            # Parse frontmatter
            fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
            if not fm_match:
                continue

            fm = fm_match.group(1)
            session_id = re.search(r"session_id:\s*(.+)", fm)
            title = re.search(r"title:\s*(.+)", fm)
            domains = re.search(r"domains:\s*(.+)", fm)
            pillars = re.search(r"pillars:\s*(.+)", fm)

            if not session_id or not title:
                continue

            sid = session_id.group(1).strip()
            t = title.group(1).strip()
            d = json.loads(domains.group(1).strip()) if domains else []
            p = json.loads(pillars.group(1).strip()) if pillars else []

            # Create conversation in DB
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO conversations (session_id, title, domains, pillars, status)
                           VALUES (%s, %s, %s, %s, 'completed')
                           ON CONFLICT (session_id) DO NOTHING
                           RETURNING id""",
                        (sid, t, d, p),
                    )
                    row = cur.fetchone()
                    if not row:
                        # Already synced
                        continue
                    conv_id = row[0]

                    # Parse segments
                    segment_pattern = r"### \[(\d+:\d+)\] (\w[\w-]*)\n\*\*Tags:\*\* (.*?)\n\n(.*?)(?=\n### |\n---|\Z)"
                    segments = re.findall(segment_pattern, text, re.DOTALL)
                    seq = 1
                    for time_str, seg_type, tags_str, content in segments:
                        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                        cur.execute(
                            """INSERT INTO segments (conversation_id, type, content, tags, sequence)
                               VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                            (conv_id, seg_type, content.strip(), tags, seq),
                        )
                        seg_id = cur.fetchone()[0]
                        vec = embed(content.strip())
                        _upsert_vector("segments", seg_id, vec, {
                            "conversation_id": conv_id,
                            "session_id": sid,
                            "type": seg_type,
                            "tags": tags,
                        })
                        seq += 1

                    # Parse summary
                    summary_match = re.search(r"## Summary\n\n(.*?)(?=\n## |\n---|\Z)", text, re.DOTALL)
                    if summary_match:
                        summary = summary_match.group(1).strip()
                        cur.execute(
                            """INSERT INTO summaries (conversation_id, summary, key_outcomes)
                               VALUES (%s, %s, %s) RETURNING id""",
                            (conv_id, summary, []),
                        )
                        sum_id = cur.fetchone()[0]
                        vec = embed(summary)
                        _upsert_vector("summaries", sum_id, vec, {
                            "conversation_id": conv_id,
                            "session_id": sid,
                        })

                    conn.commit()

            # Move to processed
            import shutil
            dest = os.path.join(PROCESSED_DIR, os.path.basename(filepath))
            shutil.move(filepath, dest)
            synced += 1

        except Exception as e:
            print(json.dumps({"error": str(e), "file": filepath}), file=sys.stderr)
            errors += 1

    print(json.dumps({"synced": synced, "errors": errors}))


def is_db_available():
    """Quick check if Postgres is reachable."""
    try:
        conn = get_conn()
        conn.close()
        return True
    except Exception:
        return False


# Reject smoke-test / junk titles so they never pollute the memory DB
# again (override with POS_ALLOW_TEST=1 for intentional test fixtures).
TEST_TITLE_RE = re.compile(
    r"^\s*(smoke-test|test thread|test$|test[-_ ]|study session\s*$|study time\s*$)",
    re.IGNORECASE,
)


def smart_start(title, domains=None, pillars=None, focus_mode=None):
    """Start a session — DB if available, markdown fallback if not."""
    if TEST_TITLE_RE.match(title or "") and os.getenv("POS_ALLOW_TEST") != "1":
        print(json.dumps({"error": "test-like title rejected — set "
                          "POS_ALLOW_TEST=1 to override", "title": title}))
        return None
    if is_db_available():
        return start_conversation(title, domains, pillars, focus_mode)
    else:
        session_id = str(uuid4())[:12]
        save_to_markdown(session_id, title, domains, pillars)
        return session_id


def smart_segment(session_id, content, type_="discussion", tags=None):
    """Add segment — DB if available, markdown fallback if not."""
    if is_db_available():
        add_segment(session_id, content, type_, tags)
    else:
        append_segment_md(session_id, content, type_, tags)


def smart_end(session_id, summary=None, outcomes=None):
    """End session — DB if available, markdown fallback if not."""
    if is_db_available():
        end_conversation(session_id, summary, outcomes)
    else:
        end_session_md(session_id, summary, outcomes)


# ── CLI ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Personal OS — Conversation Memory")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("start")
    p.add_argument("title")
    p.add_argument("--domains", nargs="*", default=[])
    p.add_argument("--pillars", nargs="*", default=[])
    p.add_argument("--focus", default=None)

    p = sub.add_parser("segment")
    p.add_argument("session_id")
    p.add_argument("content")
    p.add_argument("--type", default="discussion",
                   choices=["discussion", "decision", "plan-change", "insight", "action", "blocker"])
    p.add_argument("--tags", nargs="*", default=[])

    p = sub.add_parser("end")
    p.add_argument("session_id")
    p.add_argument("--summary", required=True)
    p.add_argument("--outcomes", nargs="*", default=[])

    p = sub.add_parser("topic")
    topic_sub = p.add_subparsers(dest="topic_cmd")
    tp = topic_sub.add_parser("create")
    tp.add_argument("name")
    tp.add_argument("--domain", default=None)
    tp.add_argument("--pillar", default=None)
    tp.add_argument("--description", default=None)
    tp = topic_sub.add_parser("link")
    tp.add_argument("session_id")
    tp.add_argument("topic_name")
    tp.add_argument("--relevance", default="primary")

    p = sub.add_parser("decide")
    p.add_argument("session_id")
    p.add_argument("decision")
    p.add_argument("--topic", default=None)
    p.add_argument("--context", default=None)
    p.add_argument("--from-state", dest="from_state", default=None)
    p.add_argument("--to-state", dest="to_state", default=None)

    p = sub.add_parser("pointer")
    p.add_argument("session_id")
    p.add_argument("content")
    p.add_argument("--type", default="insight", choices=["insight", "action", "idea", "reference", "learning"])
    p.add_argument("--topic", default=None)
    p.add_argument("--domain", default=None)
    p.add_argument("--pillar", default=None)

    p = sub.add_parser("merge-pointer")
    p.add_argument("pointer_id", type=int)
    p.add_argument("into_id", type=int)

    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=5)

    p = sub.add_parser("search-segments")
    p.add_argument("query")
    p.add_argument("--type", default=None,
                   choices=["discussion", "decision", "plan-change", "insight", "action", "blocker"])
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("search-pointers")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("timeline")
    p.add_argument("topic_name")

    p = sub.add_parser("decisions")
    p.add_argument("--topic", default=None)

    p = sub.add_parser("pointers")
    p.add_argument("--topic", default=None)
    p.add_argument("--type", default=None)

    p = sub.add_parser("recent")
    p.add_argument("--limit", type=int, default=10)

    sub.add_parser("sync")

    p = sub.add_parser("smart-start")
    p.add_argument("title")
    p.add_argument("--domains", nargs="*", default=[])
    p.add_argument("--pillars", nargs="*", default=[])
    p.add_argument("--focus", default=None)

    p = sub.add_parser("smart-segment")
    p.add_argument("session_id")
    p.add_argument("content")
    p.add_argument("--type", default="discussion",
                   choices=["discussion", "decision", "plan-change", "insight", "action", "blocker"])
    p.add_argument("--tags", nargs="*", default=[])

    p = sub.add_parser("smart-end")
    p.add_argument("session_id")
    p.add_argument("--summary", required=True)
    p.add_argument("--outcomes", nargs="*", default=[])

    sub.add_parser("check-db")

    args = parser.parse_args()

    if args.command == "start":
        start_conversation(args.title, args.domains, args.pillars, args.focus)
    elif args.command == "segment":
        add_segment(args.session_id, args.content, args.type, args.tags)
    elif args.command == "end":
        end_conversation(args.session_id, args.summary, args.outcomes)
    elif args.command == "topic":
        if args.topic_cmd == "create":
            create_topic(args.name, args.domain, args.pillar, args.description)
        elif args.topic_cmd == "link":
            link_topic(args.session_id, args.topic_name, args.relevance)
    elif args.command == "decide":
        add_decision(args.session_id, args.decision, args.topic, args.context, args.from_state, args.to_state)
    elif args.command == "pointer":
        add_pointer(args.session_id, args.content, args.type, args.topic, args.domain, args.pillar)
    elif args.command == "merge-pointer":
        merge_pointer(args.pointer_id, args.into_id)
    elif args.command == "search":
        search_summaries(args.query, args.limit)
    elif args.command == "search-segments":
        search_segments(args.query, args.type, args.limit)
    elif args.command == "search-pointers":
        search_pointers(args.query, args.limit)
    elif args.command == "timeline":
        get_timeline(args.topic_name)
    elif args.command == "decisions":
        list_decisions(args.topic)
    elif args.command == "pointers":
        list_pointers(args.topic, args.type)
    elif args.command == "recent":
        recent_conversations(args.limit)
    elif args.command == "sync":
        sync_pending()
    elif args.command == "smart-start":
        smart_start(args.title, args.domains, args.pillars, args.focus)
    elif args.command == "smart-segment":
        smart_segment(args.session_id, args.content, args.type, args.tags)
    elif args.command == "smart-end":
        smart_end(args.session_id, args.summary, args.outcomes)
    elif args.command == "check-db":
        print(json.dumps({"available": is_db_available()}))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
