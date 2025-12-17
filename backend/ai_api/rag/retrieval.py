from __future__ import annotations
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
from ai_api.rag.vector import from_f32_blob, l2_norm, cosine_sim

def retrieve(con, embeddings_client, query: str, top_k: int, min_similarity: float, min_confidence: float) -> List[Dict[str, Any]]:
    q_emb = embeddings_client.embed(query)
    q_norm = l2_norm(q_emb)
    now = datetime.now(timezone.utc).isoformat()

    rows = con.execute(
        """
        SELECT id, text, embedding, embedding_dim, embedding_norm, confidence
        FROM rag_chunks
        WHERE confidence >= ?
          AND (valid_to IS NULL OR valid_to > ?)
        ORDER BY created_at DESC
        LIMIT 2000
        """, (float(min_confidence), now)
    ).fetchall()

    scored: List[Tuple[float,int,str]] = []
    for r in rows:
        emb = from_f32_blob(r["embedding"], int(r["embedding_dim"]))
        sim = cosine_sim(q_emb, emb, q_norm, float(r["embedding_norm"]))
        if sim >= min_similarity:
            scored.append((sim, int(r["id"]), r["text"]))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"similarity": s, "chunk_id": cid, "text": txt} for s,cid,txt in scored[:top_k]]
