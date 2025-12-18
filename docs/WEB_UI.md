# Web UI

The Web UI is **optional** and designed as a thin client for the backend API.

## Features

- Chat streaming (SSE)
- TTS with OPUS → MP3 fallback
- **Speech-to-Text (STT)** via microphone
- Audio interruption on typing
- No frontend context or memory

## Speech-to-Text

- Uses browser `MediaRecorder`
- Records short audio clips (`audio/webm`)
- Sends to `/v1/audio/transcriptions`
- The transcribed text is inserted into the input box
