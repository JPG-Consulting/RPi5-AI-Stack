# API Consumption

The API is OpenAI-compatible.

Base URL:
http://<pi-ip>/v1

Supported endpoints:
- /chat/completions
- /audio/transcriptions
- /audio/speech

Streaming is supported for chat and TTS.

## Web UI

If installed, the Web UI is served at:

- `http://<pi-ip>/`

and consumes the same API under `/v1/*`.
