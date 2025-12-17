from __future__ import annotations
import json, uuid
from typing import Optional, Dict, Any
from ai_api.db import tx
from ai_api.timeutil import now_utc_iso
from ai_api.rag.chunking import chunk_text
from ai_api.rag.vector import to_f32_blob, l2_norm

def ingest_document(con, embeddings_client, text: str, doc_id: Optional[str], confidence: float, source: str, metadata: Dict[str, Any] | None):
    if confidence <= 0.0:
        return {"accepted": False, "reason": "low_confidence"}
    doc_id = doc_id or str(uuid.uuid4())
    chunks = chunk_text(text)
    if not chunks:
        return {"accepted": False, "reason": "empty"}
    meta_json = json.dumps(metadata or {}, ensure_ascii=False)
    valid_from, valid_to = now_utc_iso(), None

    with tx(con) as cur:
        for idx, ch in enumerate(chunks):
            emb = embeddings_client.embed(ch)
            cur.execute(
                """
                INSERT INTO rag_chunks (doc_id, chunk_index, text, embedding, embedding_dim, embedding_norm,
                                       created_at, valid_from, valid_to, confidence, source, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (doc_id, idx, ch, to_f32_blob(emb), len(emb), float(l2_norm(emb)), now_utc_iso(), valid_from, valid_to, float(confidence), source, meta_json)
            )
    return {"accepted": True, "doc_id": doc_id, "chunks": len(chunks)}
