# API Consumption Guide – Pi AI Stack

This document describes how to consume the **Pi AI Stack API** from real clients.

The API is **OpenAI-compatible** and designed to be a drop-in replacement for most OpenAI SDKs, with additional local capabilities.

All endpoints are exposed via **Nginx** on the local network.

---

## Base URL

```
http://<raspberry-ip>/v1
```

---

## 1. Chat Completions

### Endpoint

```
POST /v1/chat/completions
```

This endpoint is compatible with the OpenAI Chat Completions API.

It supports:

* standard (non-streaming) responses
* **streaming responses via Server-Sent Events (SSE)**

---

### Basic Request (Non-streaming)

```bash
curl http://<raspberry-ip>/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local",
    "messages": [
      {"role": "user", "content": "Hola"}
    ]
  }'
```

---

### Streaming Request (SSE)

```bash
curl http://<raspberry-ip>/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local",
    "stream": true,
    "messages": [
      {"role": "user", "content": "Hola"}
    ]
  }'
```

#### Streaming Format

The response is sent as **Server-Sent Events**:

```
data: {"choices":[{"delta":{"content":"Hola"}}]}

data: {"choices":[{"delta":{"content":" mundo"}}]}

data: [DONE]
```

---

### Conversation Handling

* Each conversation is identified by a `conversation_id`
* If omitted, the backend automatically creates a new conversation
* Clients should reuse the provided `conversation_id` in subsequent requests

Example:

```json
{
  "conversation_id": "c8a7f8a4-...",
  "messages": [...]
}
```

Conversations:

* are persisted in SQLite
* expire after a configurable inactivity TTL
* are never implicitly resurrected after expiration

---

### Client-Initiated Cancellation

If the client aborts a streaming request:

* generation stops immediately
* no fallback is triggered
* no partial output is persisted

Clients are expected to cancel streaming requests when:

* the user starts typing
* a new request is issued
* the UI explicitly interrupts playback

---

## 2. Text-to-Speech (TTS)

### Endpoint

```
POST /v1/audio/speech
```

The TTS endpoint supports **real-time audio streaming** using HTTP chunked transfer encoding.

Audio data is sent as soon as it is generated.

---

### Request Body

```json
{
  "input": "Hola mundo",
  "voice": "default",
  "response_format": "opus"
}
```

---

### Supported Formats

| Format | Description                        | Typical Use                    |
| ------ | ---------------------------------- | ------------------------------ |
| `mp3`  | Universal compatibility            | Browsers, general clients      |
| `opus` | Low-latency compressed audio (OGG) | Voice assistants, real-time UX |
| `pcm`  | Raw PCM (s16le, mono)              | Embedded / low-level devices   |

---

## 3. PCM Audio Output (Raw)

PCM output is intended for **simple or embedded clients** that cannot decode compressed audio formats.

### Characteristics

* Raw signed 16-bit little-endian PCM (`s16le`)
* Mono channel
* No container / no header
* Streamed incrementally

The client **must know the audio parameters in advance**.

### Audio Parameters

| Parameter   | Value                                |
| ----------- | ------------------------------------ |
| Encoding    | Signed 16-bit little-endian          |
| Channels    | 1 (mono)                             |
| Sample rate | Model-dependent (typically 22050 Hz) |

The server includes the sample rate in the response headers:

```
X-Audio-Sample-Rate: 22050
```

---

### PCM Request Example

```bash
curl -X POST http://<raspberry-ip>/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hola, esto es una prueba",
    "response_format": "pcm"
  }'
```

### Playback on Linux

```bash
curl -X POST http://<raspberry-ip>/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Hola mundo","response_format":"pcm"}' \
| aplay -f S16_LE -r 22050 -c 1
```

---

## 4. MP3 Example

```bash
curl -X POST http://<raspberry-ip>/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hola mundo",
    "response_format": "mp3"
  }' \
  --output out.mp3
```

---

## 5. OPUS Example (Low Latency)

```bash
curl -X POST http://<raspberry-ip>/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hola mundo",
    "response_format": "opus"
  }' \
  --output out.ogg
```

---

## 6. Speech-to-Text (STT)

### Endpoint

```
POST /v1/audio/transcriptions
```

The STT endpoint is compatible with the OpenAI Transcriptions API.

### Behavior

* Audio is processed in **batch mode** using Whisper
* The API returns a **final transcription only**
* No true streaming transcription is exposed

The Web UI may display partial results by chunking audio internally (pseudo-streaming), but this is a **UI feature**, not an API guarantee.

---

## 7. Streaming & Performance Notes

* Nginx buffering is disabled for all streaming endpoints
* Latency depends on:

  * model speed
  * hardware load
  * audio format (OPUS < MP3 < PCM)

OPUS is recommended for real-time voice interactions.

---

## 8. Error Handling & Fallback

* Client-initiated cancellation is not an error
* Cancellation never triggers fallback to OpenAI
* Fallback (if enabled) is only used for low-confidence or invalid responses

---

## 9. Security Notes

* The API is LAN-only by default
* No authentication is enabled by default
* If exposed beyond LAN, TLS and authentication are required

---

## 10. Summary

The Pi AI Stack API provides:

* OpenAI-compatible chat completions
* Real-time streaming (text and audio)
* Local-first STT and TTS
* Explicit cancellation semantics
* Predictable conversation lifecycle

Clients can safely integrate using existing OpenAI SDKs while benefiting from local execution.
