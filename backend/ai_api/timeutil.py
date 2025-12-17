from __future__ import annotations
from datetime import datetime, timezone

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s)
