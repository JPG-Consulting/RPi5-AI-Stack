from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import os, sqlite3
from ai_api.db import tx
from ai_api.timeutil import utcnow

@dataclass
class RetentionConfig:
    ttl_hours: int
    grace_period_hours: int

@dataclass
class StorageLimits:
    max_db_size_mb: int
    max_rag_entries: int

def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _cutoff(ttl_h: int) -> str:
    return (utcnow() - timedelta(hours=ttl_h)).isoformat()

def expire_conversations(con: sqlite3.Connection, cfg: RetentionConfig) -> int:
    with tx(con) as cur:
        cur.execute("""UPDATE conversations SET status='expired' WHERE status='active' AND last_activity_at < ?""", (_cutoff(cfg.ttl_hours),))
        return cur.rowcount or 0

def delete_old_conversations(con: sqlite3.Connection, cfg: RetentionConfig) -> int:
    with tx(con) as cur:
        cur.execute("""DELETE FROM conversations WHERE last_activity_at < ?""", (_cutoff(cfg.ttl_hours + cfg.grace_period_hours),))
        return cur.rowcount or 0

def delete_expired_knowledge(con: sqlite3.Connection) -> int:
    now = _iso_now()
    with tx(con) as cur:
        cur.execute("""DELETE FROM knowledge_entries WHERE valid_to IS NOT NULL AND valid_to < ?""", (now,))
        return cur.rowcount or 0

def delete_expired_rag(con: sqlite3.Connection) -> int:
    now = _iso_now()
    with tx(con) as cur:
        cur.execute("""DELETE FROM rag_chunks WHERE valid_to IS NOT NULL AND valid_to < ?""", (now,))
        return cur.rowcount or 0

def count_rag(con: sqlite3.Connection) -> int:
    row = con.execute("SELECT COUNT(1) AS c FROM rag_chunks").fetchone()
    return int(row["c"]) if row else 0

def db_size_mb(path: str) -> float:
    try:
        return os.path.getsize(path) / (1024*1024)
    except FileNotFoundError:
        return 0.0

def enforce_limits(con: sqlite3.Connection, db_path: str, limits: StorageLimits) -> dict:
    res = {"limit_triggered": False, "steps": []}
    if db_size_mb(db_path) <= limits.max_db_size_mb and count_rag(con) <= limits.max_rag_entries:
        return res
    res["limit_triggered"] = True

    # Trim oldest rag chunks if over limit
    rag_n = count_rag(con)
    if rag_n > limits.max_rag_entries:
        to_del = rag_n - limits.max_rag_entries
        with tx(con) as cur:
            cur.execute("""DELETE FROM rag_chunks WHERE id IN (SELECT id FROM rag_chunks ORDER BY created_at ASC LIMIT ?)""", (int(to_del),))
            res["steps"].append({"delete_oldest_rag_chunks": cur.rowcount or 0})

    res["final_db_size_mb"] = db_size_mb(db_path)
    res["final_rag_entries"] = count_rag(con)
    return res

def run_gc_once(con: sqlite3.Connection, db_path: str, retention: RetentionConfig, limits: StorageLimits) -> dict:
    out = {"ts": _iso_now(), "results": {}}
    out["results"]["expired_conversations"] = expire_conversations(con, retention)
    out["results"]["deleted_conversations"] = delete_old_conversations(con, retention)
    out["results"]["deleted_expired_knowledge"] = delete_expired_knowledge(con)
    out["results"]["deleted_expired_rag"] = delete_expired_rag(con)
    out["results"]["limits"] = enforce_limits(con, db_path, limits)
    return out
