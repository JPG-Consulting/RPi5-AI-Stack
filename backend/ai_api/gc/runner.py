from __future__ import annotations
import asyncio
from time import perf_counter
from ai_api.gc.retention import run_gc_once, RetentionConfig, StorageLimits
from ai_api.observability.metrics import metrics

async def periodic_gc_task(app, interval_minutes: int):
    while True:
        t0 = perf_counter()
        try:
            cfg = app.state.cfg
            res = run_gc_once(
                con=app.state.db,
                db_path=app.state.db_path,
                retention=RetentionConfig(cfg.conversation.ttl_hours, cfg.conversation.grace_period_hours),
                limits=StorageLimits(cfg.storage.max_db_size_mb, cfg.storage.max_rag_entries),
            )
            app.state.last_gc_result = res
            metrics.inc("gc_runs_total")
            metrics.observe_ms("gc_duration_ms", (perf_counter() - t0)*1000)
        except Exception:
            metrics.inc("gc_errors_total")
        finally:
            await asyncio.sleep(max(10, interval_minutes*60))
