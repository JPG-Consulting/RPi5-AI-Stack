from __future__ import annotations
import json
from datetime import datetime, timezone, timedelta
from ai_api.db import tx
from ai_api.timeutil import now_utc_iso

def _now():
    return datetime.now(timezone.utc)

def validity_for_fact(fact_type: str) -> tuple[str, str | None]:
    start = now_utc_iso()
    if fact_type == "static":
        return (start, None)
    if fact_type == "semi_static":
        end = (_now() + timedelta(days=365)).isoformat()
        return (start, end)
    return (start, None)

def upsert_knowledge_entry(con, subject: str, predicate: str, object_: str, fact_type: str, confidence: float, source: str, metadata: dict):
    valid_from, valid_to = validity_for_fact(fact_type)
    meta_json = json.dumps(metadata or {}, ensure_ascii=False)
    with tx(con) as cur:
        cur.execute(
            """
            INSERT INTO knowledge_entries (subject, predicate, object, fact_type, confidence, valid_from, valid_to, source, created_at, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(subject, predicate) DO UPDATE SET
              object=excluded.object,
              fact_type=excluded.fact_type,
              confidence=excluded.confidence,
              valid_from=excluded.valid_from,
              valid_to=excluded.valid_to,
              source=excluded.source,
              created_at=excluded.created_at,
              metadata_json=excluded.metadata_json
            """,
            (subject, predicate, object_, fact_type, float(confidence), valid_from, valid_to, source, now_utc_iso(), meta_json),
        )
