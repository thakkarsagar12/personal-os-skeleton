#!/usr/bin/env python3
"""
Personal OS — Repo RAG Indexer

Indexes markdown files in the repository into Qdrant for semantic retrieval.
Chunks files by H2 heading, attaches frontmatter + derived metadata.

Usage:
    python repo_index.py index                       # full re-index
    python repo_index.py index --changed-since N     # only files modified in last N hours
    python repo_index.py search "query"              # top-5 semantic matches
    python repo_index.py search "query" --domain study --top 5
    python repo_index.py search "query" --status active
    python repo_index.py status                      # collection stats
    python repo_index.py clear                       # wipe collection (confirm)
    python repo_index.py list-domains                # what's indexed per domain

Qdrant collection: personal_os_repo
Embedding: all-MiniLM-L6-v2 (384 dim, matches memory.py)
"""

import argparse
import hashlib
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_HTTP_PORT", "$QDRANT_PORT"))
COLLECTION = "personal_os_repo"

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent

# Lazy-loaded
_model = None
_qdrant = None

# Skip rules
SKIP_DIR_NAMES = {
    ".git", ".claude", "node_modules", "__pycache__",
    "archive", "docker-data", "processed", "pending",
    ".venv", "venv", "dist", "build",
}
SKIP_FILES = {"Demo Database.md"}
MAX_FILE_BYTES = 1_000_000  # skip > 1MB (sacred texts)
MIN_CHUNK_CHARS = 80

DOMAIN_MAP = [
    ("daily-ops/", "daily-ops"),
    ("second-brain/", "brain"),
    ("social-media/", "social"),
    ("career/", "career"),
    ("family/", "family"),
    ("study/", "study"),
    ("PERSONAL_VAULT/", "astro"),
    ("system/", "system"),
]


# ── Lazy connectors ──────────────────────────────────────────

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
        from qdrant_client.models import Distance, VectorParams
        _qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        existing = {c.name for c in _qdrant.get_collections().collections}
        if COLLECTION not in existing:
            _qdrant.create_collection(
                collection_name=COLLECTION,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
    return _qdrant


def embed(text):
    return get_model().encode(text).tolist()


# ── File walker ──────────────────────────────────────────────

def domain_of(path_rel):
    for prefix, name in DOMAIN_MAP:
        if path_rel.startswith(prefix):
            return name
    return "root"


def iter_markdown(root, changed_since_hours=None):
    cutoff = None
    if changed_since_hours is not None:
        cutoff = datetime.now() - timedelta(hours=changed_since_hours)
    for p in root.rglob("*.md"):
        if any(part in SKIP_DIR_NAMES for part in p.parts):
            continue
        if p.name in SKIP_FILES:
            continue
        try:
            st = p.stat()
        except OSError:
            continue
        if st.st_size > MAX_FILE_BYTES:
            continue
        if cutoff is not None:
            if datetime.fromtimestamp(st.st_mtime) < cutoff:
                continue
        yield p


# ── Parsing ──────────────────────────────────────────────────

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith("#"):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, text[m.end():]


def chunk_by_h2(text):
    """Split text into chunks by H2 heading. Body before first H2 is chunk 0 (heading=None)."""
    chunks = []
    current_head = None
    current_lines = []
    for line in text.splitlines(keepends=True):
        if line.startswith("## ") and not line.startswith("### "):
            if current_lines:
                body = "".join(current_lines).strip()
                if body:
                    chunks.append((current_head, body))
            current_head = line[3:].strip()
            current_lines = [line]
        else:
            current_lines.append(line)
    if current_lines:
        body = "".join(current_lines).strip()
        if body:
            chunks.append((current_head, body))
    return [(h, b) for h, b in chunks if len(b) >= MIN_CHUNK_CHARS]


def point_id(path_rel, heading):
    raw = f"{path_rel}||{heading or 'root'}"
    return int(hashlib.md5(raw.encode()).hexdigest()[:16], 16) % (2**63 - 1)


# ── Commands ─────────────────────────────────────────────────

def cmd_index(changed_since=None):
    from qdrant_client.models import PointStruct
    qdrant = get_qdrant()
    files_indexed = 0
    chunks_indexed = 0
    files_skipped = 0
    for p in iter_markdown(PROJECT_DIR, changed_since_hours=changed_since):
        path_rel = str(p.relative_to(PROJECT_DIR))
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            files_skipped += 1
            continue
        fm, body = parse_frontmatter(text)
        chunks = chunk_by_h2(body)
        if not chunks:
            body_stripped = body.strip()
            if len(body_stripped) >= MIN_CHUNK_CHARS:
                chunks = [(None, body_stripped)]
            else:
                files_skipped += 1
                continue
        mtime = datetime.fromtimestamp(p.stat().st_mtime).isoformat()
        points = []
        for heading, content in chunks:
            pid = point_id(path_rel, heading)
            embed_input = (heading + "\n" if heading else "") + content
            vec = embed(embed_input[:4000])
            payload = {
                "path": path_rel,
                "heading": heading or "",
                "content": content[:2000],
                "domain": domain_of(path_rel),
                "mtime": mtime,
                "tags": fm.get("tags", ""),
                "status": fm.get("status", ""),
                "class": fm.get("class", ""),
            }
            points.append(PointStruct(id=pid, vector=vec, payload=payload))
        if points:
            qdrant.upsert(collection_name=COLLECTION, points=points)
            files_indexed += 1
            chunks_indexed += len(points)
    scope = f"changed in last {changed_since}h" if changed_since else "full"
    print(f"[{scope}] Indexed {files_indexed} files → {chunks_indexed} chunks. Skipped {files_skipped}.")


def cmd_search(query, domain=None, status=None, top=5):
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    qdrant = get_qdrant()
    must = []
    if domain:
        must.append(FieldCondition(key="domain", match=MatchValue(value=domain)))
    if status:
        must.append(FieldCondition(key="status", match=MatchValue(value=status)))
    q_filter = Filter(must=must) if must else None
    results = qdrant.query_points(
        collection_name=COLLECTION,
        query=embed(query),
        limit=top,
        query_filter=q_filter,
    ).points
    if not results:
        print("(no matches)")
        return
    for r in results:
        p = r.payload
        heading = p.get("heading") or "(top)"
        snippet = p.get("content", "")[:260].replace("\n", " ")
        print(f"\n[{r.score:.3f}] {p['path']} :: {heading}")
        print(f"  domain={p.get('domain','')} | mtime={p.get('mtime','')[:10]}")
        print(f"  {snippet}...")


def cmd_status():
    qdrant = get_qdrant()
    info = qdrant.get_collection(COLLECTION)
    print(f"Collection:    {COLLECTION}")
    print(f"Points:        {info.points_count}")
    print(f"Vectors size:  {info.config.params.vectors.size}")
    print(f"Distance:      {info.config.params.vectors.distance}")


def cmd_list_domains():
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    qdrant = get_qdrant()
    for _, dom in DOMAIN_MAP:
        count = qdrant.count(
            collection_name=COLLECTION,
            count_filter=Filter(must=[FieldCondition(key="domain", match=MatchValue(value=dom))]),
            exact=True,
        ).count
        print(f"{dom:15s} {count}")


def cmd_clear():
    from qdrant_client.models import Distance, VectorParams
    confirm = input(f"Delete all points in '{COLLECTION}'? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return
    qdrant = get_qdrant()
    qdrant.delete_collection(COLLECTION)
    qdrant.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
    print(f"Cleared {COLLECTION}.")


def main():
    parser = argparse.ArgumentParser(description="Personal OS repo RAG indexer")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_index = sub.add_parser("index", help="(re)index repo markdown")
    p_index.add_argument("--changed-since", type=int, default=None,
                         help="only re-index files modified in last N hours")

    p_search = sub.add_parser("search", help="semantic search")
    p_search.add_argument("query")
    p_search.add_argument("--domain", default=None)
    p_search.add_argument("--status", default=None)
    p_search.add_argument("--top", type=int, default=5)

    sub.add_parser("status", help="collection stats")
    sub.add_parser("list-domains", help="count per domain")
    sub.add_parser("clear", help="wipe collection")

    args = parser.parse_args()
    if args.cmd == "index":
        cmd_index(changed_since=args.changed_since)
    elif args.cmd == "search":
        cmd_search(args.query, domain=args.domain, status=args.status, top=args.top)
    elif args.cmd == "status":
        cmd_status()
    elif args.cmd == "list-domains":
        cmd_list_domains()
    elif args.cmd == "clear":
        cmd_clear()


if __name__ == "__main__":
    main()
