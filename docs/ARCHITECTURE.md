# Architecture

Pi AI Stack is a local-first AI system composed of well-defined layers, each with strict responsibilities.

## High-level components

- **Nginx**
  - Single entry point
  - Handles LAN exposure, hardening, and streaming pass-through

- **FastAPI Backend**
  - OpenAI-compatible API (`/v1/*`)
  - Chat, STT, TTS
  - Conversation control
  - RAG + Facts pipeline
  - GC and observability

- **LLM Runtime**
  - Ollama (local)
  - Models configurable via `config.yaml`
  - OpenAI used only as optional fallback (never automatic for embeddings)

- **Persistence**
  - SQLite
  - Conversations, messages
  - RAG chunks
  - Knowledge facts
  - User memory

## Request lifecycle (chat)

1. Client sends `/v1/chat/completions`
2. ConversationControl interprets control utterances
3. ContextAssembler builds token-bounded context
4. Facts and RAG injected (if enabled)
5. Ollama generates response (streaming)
6. Client cancellation immediately stops generation
7. Post-response background tasks:
   - Facts extraction
   - RAG ingestion (if applicable)

**Important rule**: client cancellation is NOT an error and MUST NOT trigger fallback.

## Design goals

- Explicit over implicit
- Deterministic behavior
- Long-term correctness
- No silent degradation
