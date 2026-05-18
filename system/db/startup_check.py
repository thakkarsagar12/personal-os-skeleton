#!/usr/bin/env python3
"""Best-effort infra reachability report. Never fails the boot."""
import os, socket, sys


def reachable(host, port):
    try:
        with socket.create_connection((host, int(port)), timeout=2):
            return True
    except (OSError, ValueError, TypeError, OverflowError):
        return False


pg = os.environ.get("POSTGRES_PORT", "5432")
qd = os.environ.get("QDRANT_PORT", "6333")
print(f"postgres localhost:{pg} -> {'UP' if reachable('localhost', pg) else 'DOWN'}")
print(f"qdrant   localhost:{qd} -> {'UP' if reachable('localhost', qd) else 'DOWN'}")
sys.exit(0)
