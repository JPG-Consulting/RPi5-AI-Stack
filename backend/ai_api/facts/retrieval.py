from __future__ import annotations
from datetime import datetime, timezone

def get_user_facts(con, subject: str, max_items: int, min_conf: float) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    rows = con.execute(
        """
        SELECT predicate, object, fact_type, confidence
        FROM knowledge_entries
        WHERE subject=?
          AND confidence >= ?
          AND (valid_to IS NULL OR valid_to > ?)
          AND fact_type IN ('static','semi_static')
        ORDER BY confidence DESC, created_at DESC
        LIMIT ?
        """, (subject, float(min_conf), now, int(max_items))
    ).fetchall()
    return [dict(r) for r in rows]
