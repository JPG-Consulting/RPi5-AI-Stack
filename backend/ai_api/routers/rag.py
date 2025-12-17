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
    cfg = req.app.state.cfg
    if not cfg.rag.enabled:
        return {"accepted": False, "reason": "rag_disabled"}
    return ingest_document(
        con=req.app.state.db,
        embeddings_client=req.app.state.rag_embeddings,
        text=body.text,
        doc_id=body.doc_id,
        confidence=body.confidence,
        source=body.source,
        metadata=body.metadata,
    )
