# PROJECT_CONTEXT.md

## Project: RPi5 AI Stack

### Purpose
RPi5 AI Stack is a **fully local, OpenAI-compatible AI assistant platform** designed to run on a **Raspberry Pi 5 (8GB)**.
Its goal is to provide a production-grade, always-on local AI system with chat, speech-to-text (STT), and text-to-speech (TTS), while remaining extensible for future RAG, memory, and policy systems.

This project prioritizes **correctness, explicitness, and debuggability** over cleverness.

---

## High-Level Architecture

```
[ Browser / Client ]
        |
        v
[ Nginx Reverse Proxy ]
        |
        v
[ FastAPI Backend (OpenAI-compatible) ]
        |
        +--> Ollama (LLMs)
        +--> Whisper (STT)
        +--> Piper (TTS)
        +--> SQLite (conversation, memory, future RAG)
```

Key rule:
> The FastAPI backend is the single source of truth.
> The Web UI is a thin client.

---

## Backend Layout

```
backend/
└── ai_api/
    ├── main.py
    ├── config.py
    ├── routers/
    │   ├── chat.py
    │   ├── audio.py
    ├── llm/
    │   └── ollama_client.py
    ├── stt/
    │   └── whisper_engine.py
    ├── tts_engine.py
    ├── context/
    │   └── context_assembler.py
    ├── conversation/
    │   └── control.py
```

Critical rule:
Do **not** invent new configuration helpers.
Use `load_config()` from `ai_api.config`.

---

## Configuration Model

- File-based configuration only
- Root file: `config.yaml`
- Loaded via absolute path derived from `__file__`
- Required due to systemd WorkingDirectory uncertainty

---

## OpenAI Compatibility

### Chat
`POST /v1/chat/completions`
- Supports streaming and non-streaming

### Text-to-Speech
`POST /v1/audio/speech`
- Formats: `mp3`, `opus`, `pcm`
- Browser: non-streaming only
- Embedded: streaming allowed

### Speech-to-Text
`POST /v1/audio/transcriptions`
- Multipart upload
- Returns `{ "text": "..." }`

Breaking these endpoints is a regression.

---

## Streaming Rules

- Chat text: streaming OK
- Browser TTS: no streaming
- Embedded TTS: streaming OK

---

## Web UI

- Thin client
- No business logic
- Audio must be triggered by user interaction

---

## Installation

- `install.sh` is idempotent
- Explicit checks
- Robust Ollama installation
- Services: `ollama`, `pi-ai-stack`, `nginx`

---

## Design Intent

Non-goals:
- Magic behavior
- Hidden fallbacks

Goals:
- Explicitness
- Stability
- OpenAI compatibility

Correctness > Cleverness.

---

## Guidance for AI Assistants

- Respect architecture
- Avoid regressions
- Prefer minimal changes
- Preserve OpenAI semantics

---

End of document.
