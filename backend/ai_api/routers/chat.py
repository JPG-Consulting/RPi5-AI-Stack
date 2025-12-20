from __future__ import annotations
import json, uuid
import httpx
from time import perf_counter
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse

from ai_api.config import AppCfg
from ai_api.db import tx
from ai_api.timeutil import now_utc_iso, parse_iso, utcnow
from ai_api.exceptions import ClientDisconnected
from ai_api.conversation_control import decide
from ai_api.context_assembler import assemble
from ai_api.observability.metrics import metrics
from ai_api.rag.retrieval import retrieve
from ai_api.facts.retrieval import get_user_facts
from ai_api.facts.pipeline import run_facts_pipeline
from ai_api.facts.extractor import extract_facts_ollama
from ai_api.facts.l2_scorer import score_l2_ollama

router = APIRouter()

def _ensure_conversation(con, cfg: AppCfg, conversation_id: str | None) -> str:
    now = utcnow()
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    row = con.execute("SELECT * FROM conversations WHERE id=?", (conversation_id,)).fetchone()
    if row is None:
        with tx(con) as cur:
            cur.execute("INSERT INTO conversations (id, created_at, last_activity_at, status) VALUES (?, ?, ?, ?)",
                        (conversation_id, now_utc_iso(), now_utc_iso(), "active"))
        return conversation_id

    last = parse_iso(row["last_activity_at"])
    age_h = (now - last).total_seconds() / 3600.0
    if age_h > cfg.conversation.ttl_hours:
        with tx(con) as cur:
            cur.execute("UPDATE conversations SET status='expired' WHERE id=?", (conversation_id,))
        conversation_id = str(uuid.uuid4())
        with tx(con) as cur:
            cur.execute("INSERT INTO conversations (id, created_at, last_activity_at, status) VALUES (?, ?, ?, ?)",
                        (conversation_id, now_utc_iso(), now_utc_iso(), "active"))
        return conversation_id

    with tx(con) as cur:
        cur.execute("UPDATE conversations SET last_activity_at=? WHERE id=?", (now_utc_iso(), conversation_id))
    return conversation_id

def _last_assistant_message(con, conversation_id: str) -> str | None:
    row = con.execute("SELECT content FROM messages WHERE conversation_id=? AND role='assistant' ORDER BY id DESC LIMIT 1",
                      (conversation_id,)).fetchone()
    return row["content"] if row else None

def _spoken_meta_summary(con, conversation_id: str, n: int) -> str:
    rows = con.execute("SELECT role, content FROM messages WHERE conversation_id=? AND role IN ('user','assistant') ORDER BY id DESC LIMIT ?",
                       (conversation_id, n*2)).fetchall()
    rows = list(reversed(rows))
    if not rows:
        return "Aún no hemos hablado de nada en esta conversación."
    topics = [r["content"].strip() for r in rows if r["role"] == "user" and r["content"].strip()]
    if not topics:
        return "Hemos intercambiado algunos mensajes, pero no hay preguntas claras todavía."
    return "Hemos estado hablando de: " + "; ".join(topics[-min(len(topics), 5):]) + "."

async def _disconnected(req: Request) -> bool:
    try:
        return await req.is_disconnected()  # type: ignore
    except TypeError:
        return False

@router.post("/v1/chat/completions")
async def chat_completions(req: Request, background: BackgroundTasks):
    t0 = perf_counter()
    metrics.inc("chat_requests_total")

    app = req.app
    cfg: AppCfg = app.state.cfg
    con = app.state.db

    body = await req.json()
    conversation_id = body.get("conversation_id")
    incoming_messages = body.get("messages", [])
    stream = bool(body.get("stream", False))

    # last user message content
    user_text = ""
    for m in reversed(incoming_messages):
        if m.get("role") == "user":
            user_text = m.get("content") or ""
            break

    conversation_id = _ensure_conversation(con, cfg, conversation_id)

    decision = decide(user_text)
    if decision.kind == "repeat_last":
        text = _last_assistant_message(con, conversation_id) or "No tengo una respuesta anterior para repetir."
        return JSONResponse({"id": f"chatcmpl-{uuid.uuid4().hex}", "object": "chat.completion", "conversation_id": conversation_id,
                             "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}]})

    if decision.kind == "meta_summary":
        text = _spoken_meta_summary(con, conversation_id, cfg.context.last_n_turns)
        return JSONResponse({"id": f"chatcmpl-{uuid.uuid4().hex}", "object": "chat.completion", "conversation_id": conversation_id,
                             "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}]})

    # persist user message (normal)
    with tx(con) as cur:
        cur.execute("INSERT INTO messages (conversation_id, role, content, created_at, meta_json) VALUES (?, ?, ?, ?, ?)",
                    (conversation_id, "user", user_text, now_utc_iso(), None))

    rows = con.execute("SELECT role, content FROM messages WHERE conversation_id=? ORDER BY id ASC", (conversation_id,)).fetchall()
    persisted = [{"role": r["role"], "content": r["content"]} for r in rows]
    ctx = assemble(persisted, cfg.context.last_n_turns)

    # Facts injection
    user_subject = f"user:{cfg.facts.user_id}"
    facts = get_user_facts(con, user_subject, cfg.facts.max_facts_in_prompt, cfg.facts.min_confidence_persist)
    if facts:
        block = "\n".join([f"- {x['predicate']}: {x['object']}" for x in facts])
        ctx = [{"role": "system", "content": "Known facts about the user:\n" + block}] + ctx

    # RAG injection
    if cfg.rag.enabled:
        hits = retrieve(con, app.state.rag_embeddings, user_text, cfg.rag.retrieval.top_k, cfg.rag.retrieval.min_similarity, cfg.rag.persistence.min_confidence)
        if hits:
            rag_block = "\n\n".join([f"- {h['text']}" for h in hits])
            ctx = [{"role": "system", "content": "Use the following retrieved context if relevant:\n" + rag_block}] + ctx

    # Call Ollama
    ollama_url = f"{cfg.llm.ollama.base_url.rstrip('/')}/api/chat"

    def _background_facts(assistant_text: str):
        def extractor():
            return extract_facts_ollama(cfg.llm.ollama.base_url, cfg.llm.ollama.model, 120, user_subject, user_text)
        def l2(fact_str: str, fact_type: str, evidence: str) -> float:
            return score_l2_ollama(cfg.facts.l2.ollama.base_url, cfg.facts.l2.ollama.model, cfg.facts.l2.ollama.timeout_seconds, fact_str, fact_type, evidence)
        run_facts_pipeline(con, cfg, user_subject, user_text, extractor, l2)

    if stream:
        async def sse_stream():
            try:
                full_parts = []
                async with httpx.AsyncClient(timeout=cfg.llm.ollama.timeout_seconds) as client:
                    async with client.stream("POST", ollama_url, json={"model": cfg.llm.ollama.model, "messages": ctx, "stream": True}) as r:
                        r.raise_for_status()
                        async for line in r.aiter_lines():
                            if await _disconnected(req):
                                raise ClientDisconnected()
                            if not line:
                                continue
                            data = json.loads(line)
                            if data.get("done"):
                                yield "data: [DONE]\n\n"
                                break
                            delta = (data.get("message") or {}).get("content") or ""
                            if delta:
                                full_parts.append(delta)
                                payload = {"choices": [{"delta": {"content": delta}}]}
                                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

                full = "".join(full_parts).strip()
                if full:
                    with tx(con) as cur:
                        cur.execute("INSERT INTO messages (conversation_id, role, content, created_at, meta_json) VALUES (?, ?, ?, ?, ?)",
                                    (conversation_id, "assistant", full, now_utc_iso(), None))
                    # background facts extraction (non-blocking)
                    background.add_task(_background_facts, full)

                metrics.inc("chat_success_total")
            except ClientDisconnected:
                metrics.inc("chat_cancelled_total")
                return
            except Exception:
                metrics.inc("chat_error_total")
                raise
            finally:
                metrics.observe_ms("chat_duration_ms", (perf_counter() - t0)*1000)

        return StreamingResponse(sse_stream(), media_type="text/event-stream", headers={"X-Conversation-Id": conversation_id})

    # non-stream
    async with httpx.AsyncClient(timeout=cfg.llm.ollama.timeout_seconds) as client:
        r = await client.post(ollama_url, json={"model": cfg.llm.ollama.model, "messages": ctx, "stream": False})
        r.raise_for_status()
        text = ((r.json().get("message") or {}).get("content") or "").strip()

    with tx(con) as cur:
        cur.execute("INSERT INTO messages (conversation_id, role, content, created_at, meta_json) VALUES (?, ?, ?, ?, ?)",
                    (conversation_id, "assistant", text, now_utc_iso(), None))

    background.add_task(_background_facts, text)
    metrics.inc("chat_success_total")
    metrics.observe_ms("chat_duration_ms", (perf_counter() - t0)*1000)

    return JSONResponse({"id": f"chatcmpl-{uuid.uuid4().hex}", "object": "chat.completion", "conversation_id": conversation_id,
                         "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}]})
