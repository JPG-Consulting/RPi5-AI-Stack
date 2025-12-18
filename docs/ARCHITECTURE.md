# Architecture – Pi AI Stack

This document describes the **global architecture** of the Pi AI Stack project.
It is intended to be:

- a single-page mental model of the system
- readable by humans and AI tools
- a reference for future maintenance and evolution

---

## 1. High-Level Overview

Pi AI Stack is a **local-first AI runtime** designed for Raspberry Pi 5.

It provides:

- an **OpenAI-compatible API**
- local **LLM inference** via Ollama
- local **Speech-to-Text (STT)** via Whisper
- local **Text-to-Speech (TTS)** via Piper
- governed **RAG + Facts memory**
- a lightweight **Web UI**
- full offline operation (optional cloud fallback)

All intelligence, policy, and memory live in the backend.
The Web UI is a thin client.

---

## 2. Runtime Components

```
┌────────────┐
│   Web UI   │
│ (Browser)  │
└─────┬──────┘
      │ HTTP (SSE + streaming audio)
      ▼
┌──────────────────────┐
│        Nginx         │
│  - static Web UI     │
│  - reverse proxy     │
└─────┬────────────────┘
      │ localhost
      ▼
┌──────────────────────┐
│     FastAPI App      │
│      (ai_api)        │
├──────────────────────┤
│ ConversationControl  │
│ ContextAssembler     │
│ Facts pipeline       │
│ RAG pipeline         │
│ GC / Retention       │
│ Observability        │
└─────┬────────────────┘
      │
      ▼
┌──────────────────────┐
│   Local Engines      │
│  - Ollama (LLM)      │
│  - Whisper (STT)     │
│  - Piper (TTS)       │
└──────────────────────┘
```

---

## 3. Backend Layout

```
backend/
└── ai_api/
    ├── main.py
    ├── config.py
    ├── context_assembler.py
    ├── conversation_control.py
    ├── db.py
    ├── routers/
    │   ├── chat.py
    │   └── audio.py
    ├── rag/
    ├── facts/
    ├── gc/
    └── observability/
```

Key principles:

- `ai_api` is the **only Python package**
- All policies live in backend code, not the UI
- No global state outside SQLite

---

## 4. Configuration Model

### Single source of truth

- Configuration lives in **`config.yaml` at the repo root**
- Loaded once at startup
- Strongly typed using Pydantic models

### Config loading (important)

The configuration file is **NOT loaded relative to the working directory**.

Instead, it is resolved relative to the package location:

```python
Path(__file__).resolve().parents[2] / "config.yaml"
```

This guarantees that:

- systemd
- CLI execution
- tests
- different working directories

all behave consistently.

---

## 5. Python Import Paths and systemd WorkingDirectory

The backend Python package (`ai_api`) lives under:

```
backend/ai_api
```

For this reason, the **systemd unit MUST ensure that `backend/` is present in
Python’s import path**.

The current and supported approach is:

- `WorkingDirectory` is set to `/opt/pi-ai-stack/backend`
- `uvicorn` is executed using absolute paths
- No reliance on `PYTHONPATH` is required

This guarantees that:

- `import ai_api` works reliably
- the application can be started via systemd, CLI, or tests
- no implicit assumptions about the current working directory leak into code

> ⚠️ If `WorkingDirectory` is changed to `/opt/pi-ai-stack`, the service will fail
> with `ModuleNotFoundError: No module named 'ai_api'` unless `PYTHONPATH` is
> explicitly adjusted or the package layout is changed.

The configuration file (`config.yaml`) is **not affected by the working directory**,
as it is resolved relative to the package location using `__file__`.

---

## 6. Conversation Flow

1. User sends a message
2. `ConversationControl` intercepts:
   - repeat
   - meta questions
   - normal conversation
3. `ContextAssembler` builds the prompt:
   - last N turns
   - summaries
   - facts
   - RAG entries
4. LLM is queried (Ollama)
5. Confidence scoring applied
6. Optional fallback to OpenAI (if enabled)
7. Response returned (streaming)

---

## 7. RAG and Facts Governance

### RAG
- Disabled/Enabled via config
- Embeddings stored locally
- Only high-confidence, non-dynamic knowledge persists
- TTL + GC enforced

### Facts
- Explicit extraction (rules + LLM)
- L1 (rules) + L2 (LLM validation)
- User-scoped
- Bounded in prompt size

---

## 8. Storage Model

- SQLite database
- Single file
- WAL mode
- Hard size limits
- Periodic garbage collection

No external databases are required.

---

## 9. Streaming Model

- Chat: SSE (`text/event-stream`)
- TTS:
  - OPUS streaming (preferred)
  - MP3 fallback
  - PCM supported for embedded clients
- STT:
  - Batch transcription via Whisper

Cancellation is **not an error** and does not trigger fallback.

---

## 10. Web UI Architecture

- Static files served by Nginx
- No build step
- No stateful logic
- Uses the same `/v1/*` API as any client

The Web UI is optional and replaceable.

---

## 11. Observability

- JSON metrics endpoint
- No Prometheus dependency
- Focus on:
  - usage
  - cancellations
  - confidence levels
  - RAG activity

---

## 12. Design Constraints and Non-Goals

Explicit non-goals:

- Kubernetes
- microservices
- Redis
- external vector databases
- Prometheus/Grafana

The system is designed to **age well**, not to scale infinitely.

---

## 13. Architectural Guarantees

- No implicit CWD dependencies
- No hidden memory growth
- No silent knowledge pollution
- Deterministic startup
- Offline-first

---

## 14. Status

This architecture represents a **pre-alpha but production-grade foundation**.

Future changes should:
- preserve these guarantees
- be validated by tests
- update this document when assumptions change
