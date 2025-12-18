# Architecture – Pi AI Stack

This document describes the global architecture of **Pi AI Stack**.
It is intended to be a concise but complete reference for both humans and automated tools.

---

## 1. High-Level Overview

Pi AI Stack is a **local-first AI runtime** designed to run on **Raspberry Pi 5**.

It provides:

- An **OpenAI-compatible API**
- Local **LLM inference** via Ollama
- Local **Speech-to-Text (STT)** via Whisper
- Local **Text-to-Speech (TTS)** via Piper
- Governed **RAG + Facts memory**
- A built-in **Web UI**
- Offline-first operation

The system is designed to be **predictable, secure, and easy to operate**.

---

## 2. Runtime Components

```
LAN Client / Browser
        |
        v
     Nginx :80
        |
        +--> /        -> Web UI (static)
        |
        +--> /v1/*    -> FastAPI Backend (127.0.0.1:8000)
                                |
                                v
                         Local AI Engines
                     (Ollama, Whisper, Piper)
```

---

## 3. Mandatory Reverse Proxy (Nginx)

**Nginx is a mandatory component of Pi AI Stack.**

The FastAPI backend is intentionally bound to `127.0.0.1` and is **never exposed
directly to the network**.

All external access goes through Nginx:

- `/` serves the Web UI
- `/v1/*` proxies the OpenAI-compatible API to FastAPI

This design:

- provides a single entry point
- isolates the backend from the network
- avoids exposing internal ports
- matches production-grade deployment patterns

Direct access to port `8000` from the LAN is neither required nor supported.

---

## 4. Backend Architecture

The backend is a single FastAPI service implemented as the `ai_api` Python package.

```
backend/
└── ai_api/
    ├── main.py
    ├── config.py
    ├── conversation_control.py
    ├── context_assembler.py
    ├── routers/
    ├── rag/
    ├── facts/
    ├── gc/
    └── observability/
```

Key principles:

- One backend service
- One Python package
- All intelligence and policy live in the backend

---

## 5. Configuration Model

- All configuration lives in `config.yaml` at the repository root
- Configuration is loaded once at startup
- The path to `config.yaml` is resolved using `__file__`, not the working directory

This guarantees consistent behavior across:

- systemd
- local development
- tests

---

## 6. Python Import Paths and systemd

The backend package (`ai_api`) lives under `backend/ai_api`.

The systemd unit sets:

```
WorkingDirectory=/opt/pi-ai-stack/backend
```

This ensures:

- `import ai_api` works reliably
- no `PYTHONPATH` hacks are required
- consistent imports in all environments

---

## 7. Conversation Flow

1. Client sends a request via `/v1/*`
2. Nginx proxies the request to FastAPI
3. ConversationControl classifies the request
4. ContextAssembler builds the prompt
5. LLM is queried via Ollama
6. Confidence scoring is applied
7. Optional fallback logic is evaluated
8. Response is streamed back to the client

---

## 8. Memory and Knowledge

### RAG
- Governed ingestion
- Confidence-based persistence
- TTL and garbage collection
- Local embeddings

### Facts
- Explicit extraction
- Validation (L1 + L2)
- User-scoped storage
- Bounded prompt injection

---

## 9. Storage

- SQLite (single file)
- WAL mode
- Size limits enforced
- Periodic garbage collection

No external database is required.

---

## 10. Streaming Model

- Chat responses: Server-Sent Events (SSE)
- TTS: streaming audio (OPUS, MP3, PCM)
- STT: batch transcription

Client-side interruptions are handled gracefully and do not trigger fallback.

---

## 11. Web UI

- Static client served by Nginx
- No backend logic
- No build step required
- Uses the same OpenAI-compatible API as any external client

The Web UI is a convenience layer, not a dependency of the backend.

---

## 12. Observability

- JSON-based metrics
- No Prometheus dependency
- Focus on correctness and usage visibility

---

## 13. Design Constraints

Explicit non-goals:

- Kubernetes
- Microservices
- External databases
- Exposing backend ports directly

---

## 14. Summary

Pi AI Stack follows a **single-entry-point architecture**:

- Nginx is mandatory
- Backend is isolated
- Configuration is deterministic
- The system is designed to age well

---

End of document.
