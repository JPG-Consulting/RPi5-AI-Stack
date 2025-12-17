# ARCHITECTURE – Pi AI Stack

This document describes the complete architecture of the **Pi AI Stack** as currently designed.
It is intended to be a **single source of truth** for system behavior, guarantees, and design decisions.

---

## 1. Goals & Principles

The Pi AI Stack is designed to run a **local-first, governed AI assistant** on a Raspberry Pi 5 (8 GB RAM).

Core principles:

* **Local-first**: local models by default, remote only as explicit fallback
* **OpenAI-compatible API**: drop-in replacement for OpenAI clients
* **Explicit governance**: no implicit learning, no silent state changes
* **Predictable behavior**: clear lifecycle rules, no hidden magic
* **Resource-aware**: designed for constrained hardware (Raspberry Pi)

---

## 2. High-Level Architecture

```
Client (Browser / Device)
        ↓
     Nginx
        ↓
    FastAPI (OpenAI-compatible API)
        ↓
ConversationControl
        ↓
ContextAssembler
        ↓
Local LLM (Ollama)
        ↓
Post-processing (Scoring, Memory, RAG)
        ↓
     Response
```

Nginx is the **only externally exposed service**. All other components are bound to localhost.

---

## 3. Configuration Model

All configuration is defined in a single **`config.yaml`** file.

Nothing critical is hardcoded.

Examples of configurable domains:

* LLM backend (Ollama base URL, model)
* Conversation TTL
* Context limits (tokens, last N turns)
* RAG enable/disable
* OpenAI fallback enable/disable

---

## 4. LLM Backend (Ollama)

The local LLM runtime is provided by **Ollama**.

### Key rules

* The Ollama endpoint is **never hardcoded**
* The base URL and model are resolved from `config.yaml`
* Ollama is treated as a **replaceable dependency**, even when local

This allows:

* moving Ollama to another host or container
* changing models without code changes
* mocking or stubbing Ollama in tests

---

## 5. Request Lifecycle (Chat)

```
HTTP request
   ↓
ConversationControl
   ├─ repeat_last      → return last answer (no history mutation)
   ├─ meta_summary    → spoken summary (no history mutation)
   └─ normal
        ↓
Conversation lookup / creation
        ↓
Persist user message
        ↓
Memory Extractor (explicit facts only)
        ↓
RAG retrieval (if enabled)
        ↓
ContextAssembler (token-budget aware)
        ↓
Local LLM (Ollama, streaming)
        ↓
Streaming response to client
        ↓
Scoring (confidence L1 / L2)
        ↓
Optional OpenAI fallback
        ↓
Persist assistant message
        ↓
Summarizer (incremental)
```

---

## 6. Client-Initiated Cancellation (Critical Rule)

If a client disconnects during streaming, **generation must stop immediately**.

A client-initiated cancellation is treated as a **control-flow event**, not a failure.

It must **never**:

* trigger scoring or confidence evaluation
* trigger OpenAI fallback
* retry generation
* persist partial output
* affect memory, summaries, or RAG

This rule prevents wasted CPU on the Raspberry Pi and avoids unintended external API usage.

---

## 7. Conversation Model

### Conversation Identity

* Each conversation is identified by a `conversation_id` (UUID)
* The backend creates conversations automatically
* Clients only reuse the provided `conversation_id`

### Persistence

* Conversations are persisted in **SQLite**
* Conversations survive reboot if not expired

### TTL (Expiration)

* Conversations expire after a configurable inactivity TTL
* TTL is defined in `config.yaml`

Default:

```yaml
conversation:
  ttl_hours: 24
```

Recommended range:

* minimum: 1 hour
* maximum: 168 hours (7 days)

Expired conversations are never rehydrated.

---

## 8. Conversation States

Conversations have only two states:

* `active`
* `expired`

No paused, archived, or intermediate states exist.

Expiration is evaluated lazily on access.

---

## 9. Message Persistence

### Messages Table

Messages are stored in SQLite and linked to `conversation_id`.

Stored roles:

* `user`
* `assistant`
* `system` (only if persistent)

### System Messages

Only **persistent and declarative** system messages are stored.

Stored examples:

* base assistant prompt
* fixed persona or language

Never stored:

* temporary RAG prompts
* injected summaries
* scoring instructions
* technical formatting directives

This prevents long-term context pollution.

---

## 10. Message Metadata (`meta_json`)

Messages may include optional `meta_json` metadata.

Rules:

* metadata only (JSON)
* no user text
* no assistant text
* no audio
* no prompts

Typical contents:

* model / provider used
* latency metrics
* fallback usage
* confidence scores
* cancellation markers

`meta_json` is **never** injected into:

* LLM context
* RAG
* summaries

It exists solely for observability, debugging, and regression testing.

---

## 11. Context Assembly

The `ContextAssembler` builds the LLM context using:

* running conversation summary (if present)
* the last N user/assistant turns

Limits are token-aware and configurable.

Commands handled by `ConversationControl` are **never** part of the context.

---

## 12. Audio Pipeline

### Speech-to-Text (STT)

* Engine: Whisper
* Mode: batch
* UI may show partial results (pseudo-streaming)
* API returns final transcription only

No true STT streaming is exposed.

### Text-to-Speech (TTS)

* Engine: Piper
* Streaming via chunked transfer

Supported formats:

* MP3 (default)
* OPUS (low latency)
* PCM (raw s16le mono, embedded devices)

Audio is transient and never persisted.

---

## 13. RAG & Memory

* RAG is enabled by default
* Knowledge persistence is governed by explicit policies
* Time-sensitive facts are treated differently from static knowledge
* Low-confidence or unverified information is never persisted

The system never "learns silently".

---

## 14. Observability

Observability is numeric and privacy-preserving:

* no user text stored
* no audio stored
* no prompts stored

Metrics include:

* request counts
* latency (STT / LLM / TTS)
* cancellations

---

## 15. Deployment Model

* Target platform: Raspberry Pi 5 (8 GB)
* OS: Raspberry Pi OS 64-bit
* Services managed via systemd
* Nginx is the only LAN-exposed service
* FastAPI binds to localhost only

---

## 16. System Guarantees

The Pi AI Stack guarantees:

* no silent learning
* no context contamination
* no fallback on cancellation
* deterministic conversation lifecycle
* explainable, inspectable behavior

---
