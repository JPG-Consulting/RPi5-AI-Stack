from __future__ import annotations
from typing import List

def chunk_text(text: str, max_chars: int = 900, overlap: int = 120) -> List[str]:
    t = " ".join((text or "").split())
    if not t:
        return []
    chunks = []
    i = 0
    n = len(t)
    while i < n:
        j = min(n, i + max_chars)
        ch = t[i:j].strip()
        if ch:
            chunks.append(ch)
        i = max(0, j - overlap)
        if i == j:
            break
    return chunks
