from __future__ import annotations
import sqlite3
import json
import time
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from jarvis.config import CFG
from jarvis.logger import get_logger

log = get_logger(__name__)

DB_PATH = CFG["memory"]["db_path"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    intent TEXT,
    tools_called TEXT,
    outcome TEXT
);

CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    fact TEXT NOT NULL,
    embedding BLOB,
    source TEXT DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_ts REAL NOT NULL,
    updated_ts REAL NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'todo',
    priority TEXT DEFAULT 'medium',
    due_date TEXT,
    tags TEXT
);

CREATE TABLE IF NOT EXISTS preferences (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_ts REAL NOT NULL
);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
    log.info("Database initialized", extra={"path": DB_PATH})


# ── Episodes ──────────────────────────────────────────────────────────────────

def add_episode(role: str, content: str, intent: str = None,
                tools_called: list = None, outcome: str = None):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO episodes (ts, role, content, intent, tools_called, outcome) VALUES (?,?,?,?,?,?)",
            (time.time(), role, content, intent,
             json.dumps(tools_called) if tools_called else None, outcome)
        )


def get_recent_episodes(n: int = 20) -> List[dict]:
    cutoff = (datetime.now() - timedelta(days=CFG["memory"]["max_episodic_days"])).timestamp()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM episodes WHERE ts > ? ORDER BY ts DESC LIMIT ?",
            (cutoff, n)
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def format_history_for_prompt(n: int = 10) -> str:
    eps = get_recent_episodes(n)
    lines = []
    for ep in eps:
        prefix = "User" if ep["role"] == "user" else "Jarvis"
        lines.append(f"{prefix}: {ep['content']}")
    return "\\n".join(lines)


# ── Semantic Memory ───────────────────────────────────────────────────────────

_embedder = None

def _get_embedder():
    global _embedder
    if _embedder is None:
        log.info(f"Loading embedder: {CFG['memory']['embedding_model']}")
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer(CFG["memory"]["embedding_model"])
    return _embedder


def embed_text(text: str) -> bytes:
    emb = _get_embedder().encode(text, normalize_embeddings=True)
    return emb.astype(np.float32).tobytes()
    return _embedder


def embed_text(text: str) -> bytes:
    try:
        emb = _get_embedder().encode(text, normalize_embeddings=True)
        return emb.astype(np.float32).tobytes()
    except Exception as e:
        log.warning(f"embed_text failed: {e}")
        raise


def store_memory(fact: str, source: str = "user"):
    emb_bytes = embed_text(fact)
    with get_conn() as conn:
        count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        if count >= CFG["memory"]["max_semantic_entries"]:
            conn.execute("DELETE FROM memories WHERE id = (SELECT id FROM memories ORDER BY ts ASC LIMIT 1)")
        conn.execute(
            "INSERT INTO memories (ts, fact, embedding, source) VALUES (?,?,?,?)",
            (time.time(), fact, emb_bytes, source)
        )
    log.info(f"Stored memory: {fact[:60]}...")


def recall_memories(query: str, top_k: int = None) -> List[str]:
    return []  # Disabled: requires sentence-transformers which crashes on Windows


# ── Preferences ───────────────────────────────────────────────────────────────

def set_preference(key: str, value: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO preferences (key, value, updated_ts) VALUES (?,?,?)",
            (key, value, time.time())
        )


def get_preference(key: str, default: str = None) -> Optional[str]:
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM preferences WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def get_all_preferences() -> dict:
    with get_conn() as conn:
        rows = conn.execute("SELECT key, value FROM preferences").fetchall()
    return {r["key"]: r["value"] for r in rows}


# Tasks are managed by task_tool.py directly via get_conn()
