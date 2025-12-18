# Web UI

The Web UI is **optional** and designed as a thin client for the backend API.

## Audio strategy

1. **Primary**: OPUS streaming (`audio/ogg; codecs="opus"`) via MediaSource
2. **Fallback**: MP3 (single-shot download)

Fallback is automatic if OPUS is unsupported or fails.
