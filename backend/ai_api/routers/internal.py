from __future__ import annotations
from fastapi import APIRouter, Request
from ai_api.gc.retention import run_gc_once, RetentionConfig, StorageLimits

router = APIRouter()

@router.post("/internal/gc/run")
async def run_gc(req: Request):
    app = req.app
    cfg = app.state.cfg
    res = run_gc_once(
        con=app.state.db,
        db_path=app.state.db_path,
        retention=RetentionConfig(cfg.conversation.ttl_hours, cfg.conversation.grace_period_hours),
        limits=StorageLimits(cfg.storage.max_db_size_mb, cfg.storage.max_rag_entries),
    )
    app.state.last_gc_result = res
    return res

@router.get("/internal/gc/last")
async def last_gc(req: Request):
    return getattr(req.app.state, "last_gc_result", None) or {"status": "no_gc_run_yet"}
