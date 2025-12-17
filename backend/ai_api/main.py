from __future__ import annotations
import asyncio
from fastapi import FastAPI

from ai_api.config import load_config
from ai_api.db import open_db
from ai_api.stt_engine import WhisperSTT
from ai_api.rag.embeddings import OllamaEmbeddings, EmbeddingConfig
from ai_api.routers import chat_router, audio_router, internal_router, rag_internal_router
from ai_api.observability.endpoint import router as metrics_router
from ai_api.gc.runner import periodic_gc_task

def create_app() -> FastAPI:
    app = FastAPI(title="Pi AI Stack API")

    cfg = load_config("config.yaml")
    app.state.cfg = cfg

    app.state.db_path = cfg.storage.db_path
    app.state.db = open_db(cfg.storage.db_path)

    # STT
    app.state.stt = WhisperSTT(cfg.stt.whisper.model, cfg.stt.device, cfg.stt.compute_type)

    # RAG embeddings (single-provider rule; no fallback)
    app.state.rag_embeddings = OllamaEmbeddings(
        EmbeddingConfig(
            base_url=cfg.rag.embeddings.ollama.base_url,
            model=cfg.rag.embeddings.ollama.model,
            timeout_seconds=cfg.rag.embeddings.ollama.timeout_seconds,
        )
    )

    app.include_router(chat_router)
    app.include_router(audio_router)
    app.include_router(internal_router)
    app.include_router(rag_internal_router)

    if cfg.observability.enabled:
        app.include_router(metrics_router)

    @app.on_event("startup")
    async def _startup():
        if cfg.gc.periodic.enabled:
            app.state.gc_task = asyncio.create_task(periodic_gc_task(app, int(cfg.gc.periodic.interval_minutes)))

    return app

app = create_app()
