# Pi AI Stack – Backend Code Skeleton

This directory contains a complete **backend code skeleton** for Pi AI Stack.

- FastAPI (OpenAI-compatible)
- SQLite persistence
- Chat streaming via SSE
- TTS streaming (PCM/MP3/OPUS in OGG via ffmpeg)
- STT batch (faster-whisper)
- RAG (ingest + embeddings + retrieval) – local embeddings via Ollama
- Facts pipeline (extract + L1 + L2 + persist)
- GC (TTL + grace + hard limits)
- Observability (JSON metrics)

Configure via `config.yaml` at repo root.
