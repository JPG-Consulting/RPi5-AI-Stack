from __future__ import annotations
from fastapi import APIRouter, Request
from pydantic import BaseModel
from ai_api.rag.ingest import ingest_document

router = APIRouter()

class IngestReq(BaseModel):
    text: str
    doc_id: str | None = None
    confidence: float = 0.95
    source: str = "user_ingest"
    metadata: dict | None = None

@router.post("/internal/rag/ingest")
async def ingest(req: Request, body: IngestReq):
    app = req.app
    cfg = app.state.cfg
    if not cfg.rag.enabled:
        return {"accepted": False, "reason": "rag_disabled"}
    if not cfg.rag.persistence.enabled:
        return {"accepted": False, "reason": "rag_persistence_disabled"}
    if body.confidence < cfg.rag.persistence.min_confidence:
        return {"accepted": False, "reason": "confidence_below_threshold"}

    return ingest_document(app.state.db, app.state.rag_embeddings, body.text, body.doc_id, body.confidence, body.source, body.metadata)
