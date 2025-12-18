# Web UI

The Web UI is **optional** and designed as a thin client for the backend API.

## Goals

- ChatGPT-like experience
- Text streaming (SSE via POST `/v1/chat/completions`)
- TTS streaming (binary chunks via `/v1/audio/speech`)
- Audio interruption when the user starts typing
- No “frontend brain”: backend owns context, memory, and policies

## Tech choice (v1)

To keep Raspberry Pi deployment simple, v1 uses:

- plain HTML/CSS/ES modules
- no bundler, no npm
- served by Nginx as static files from `/opt/pi-ai-stack/web-ui`

## Runtime behavior

### Chat streaming
- UI uses `fetch()` POST and parses SSE (`data: ...` events)
- Each `delta.content` is rendered immediately
- `[DONE]` ends the stream

### TTS streaming (OPUS)
- UI requests `response_format=opus`
- Uses MediaSource (`audio/ogg; codecs="opus"`) for incremental playback
- If OPUS MSE is not supported, the UI currently skips audio (v1). (MP3 fallback can be added.)

### Interruption
When the user types or presses Stop:
- aborts the chat stream
- aborts the TTS stream
- stops audio immediately
- does not create new messages or memory entries

## Files

- `web-ui/index.html`
- `web-ui/styles.css`
- `web-ui/app.js`
- `web-ui/stream.js` – SSE parsing
- `web-ui/audio.js` – OPUS streaming player
