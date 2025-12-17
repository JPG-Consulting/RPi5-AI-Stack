# Pi AI Stack

Pi AI Stack is a **local-first AI assistant platform** designed to run on a **Raspberry Pi 5 (8 GB RAM)**.

It exposes an **OpenAI-compatible API** for chat, speech-to-text, and text-to-speech, while running fully locally by default.
The system is engineered to **age well** through explicit governance of memory, RAG, retention, and confidence scoring.

The repository is documentation-driven: using only the contents of `docs/`, a human or AI system can recreate the entire project from scratch.

## Highlights

- OpenAI-compatible REST API
- Local LLM via Ollama (configurable)
- Whisper STT (batch)
- Piper TTS (streaming: OPUS / MP3 / PCM)
- Conversation control (repeat, meta-questions, cancellation)
- Governed RAG with confidence + time awareness
- Explicit user facts pipeline (no hallucinated memory)
- SQLite persistence with GC (TTL + grace)
- Lightweight JSON observability
- Optional Web UI (ChatGPT-like)

Start with **docs/README.md**.
