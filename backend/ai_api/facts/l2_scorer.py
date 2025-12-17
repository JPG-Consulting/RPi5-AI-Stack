from __future__ import annotations
import requests

PROMPT = """Return ONLY a float between 0.0 and 1.0.
Score confidence that this fact is explicitly stated, unambiguous, and stable given its fact_type.

fact_type: {fact_type}
fact: {fact}
user_evidence: {evidence}
"""

def score_l2_ollama(base_url: str, model: str, timeout_s: int, fact_str: str, fact_type: str, evidence: str) -> float:
    url = f"{base_url.rstrip('/')}/api/chat"
    msgs = [
        {"role": "system", "content": "You are a strict scorer. Output ONLY a float."},
        {"role": "user", "content": PROMPT.format(fact_type=fact_type, fact=fact_str, evidence=evidence)},
    ]
    r = requests.post(url, json={"model": model, "messages": msgs, "stream": False}, timeout=timeout_s)
    r.raise_for_status()
    s = ((r.json().get("message") or {}).get("content") or "").strip()
    try:
        v = float(s)
        return max(0.0, min(1.0, v))
    except Exception:
        return 0.0
