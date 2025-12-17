from __future__ import annotations
import json, requests
from typing import List
from ai_api.facts.types import FactCandidate

SYSTEM = """You are a strict information extractor.
Extract ONLY explicit facts stated by the USER about themselves.
Rules:
- DO NOT infer.
- Ignore questions/commands.
- Output MUST be valid JSON (no markdown), an array of objects with keys:
  subject, predicate, object, fact_type, evidence
- fact_type must be one of: static, semi_static, dynamic
"""

def extract_facts_ollama(base_url: str, model: str, timeout_s: int, user_subject: str, user_text: str) -> List[FactCandidate]:
    url = f"{base_url.rstrip('/')}/api/chat"
    msgs = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Subject: {user_subject}\nUser message:\n{user_text}\nReturn JSON array:"},
    ]
    r = requests.post(url, json={"model": model, "messages": msgs, "stream": False}, timeout=timeout_s)
    r.raise_for_status()
    content = (r.json().get("message") or {}).get("content") or "[]"
    try:
        data = json.loads(content)
    except Exception:
        return []
    out: List[FactCandidate] = []
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            subj = str(item.get("subject") or user_subject).strip()
            pred = str(item.get("predicate") or "").strip()
            obj = str(item.get("object") or "").strip()
            ftype = str(item.get("fact_type") or "").strip()
            ev = str(item.get("evidence") or "").strip() or (user_text[:200] if user_text else "")
            if pred and obj and ftype in ("static","semi_static","dynamic"):
                out.append(FactCandidate(subj, pred, obj, ftype, ev))
    return out
