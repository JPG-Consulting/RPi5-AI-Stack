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

---

# Pi AI Stack API Reference

## Overview
Pi AI Stack exposes an OpenAI-compatible REST API for chat, speech-to-text (STT), and text-to-speech (TTS). The public
API base path is `/v1`, with internal/admin endpoints under `/internal/*`, plus optional observability metrics at
`/metrics` when enabled in configuration.

## Base URL
```
http://<pi-ip>/v1
```
All public endpoints below are rooted under this base URL unless explicitly noted (e.g., `/internal/*`, `/metrics`).

## Authentication
No authentication is enforced in the backend routers (there are no auth checks or dependencies in the handlers).

---

# Endpoints

## 1) POST `/v1/chat/completions`

### Purpose
Send a chat completion request using OpenAI-style message arrays. The server manages conversation state, injects
facts/RAG context, and returns either a full response or a streaming SSE response. It can also return special “repeat
last” or “meta summary” responses based on conversation control logic.

### Request (JSON)
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `messages` | array | **Yes (for meaningful output)** | Array of `{role, content}` objects. The handler scans the last user message to determine the prompt text. If omitted, it defaults to `[]` but will typically yield no useful response because `user_text` stays empty. |
| `conversation_id` | string | No | Reuse an existing conversation. If omitted, a new UUID is created. If an existing conversation is expired, a new UUID is generated and returned. |
| `stream` | boolean | No | Defaults to `false`. When `true`, returns Server-Sent Events (SSE) with incremental `delta` content and a `[DONE]` sentinel. Also includes `X-Conversation-Id` header in the response. |

> **Note:** Other OpenAI-style fields (like `model`) are not parsed by this handler; the server always uses configured
> Ollama settings internally.

### Response (Non-Streaming JSON)
```json
{
  "id": "chatcmpl-<uuid>",
  "object": "chat.completion",
  "conversation_id": "<uuid>",
  "choices": [
    {
      "index": 0,
      "message": { "role": "assistant", "content": "..." },
      "finish_reason": "stop"
    }
  ]
}
```

### Response (Streaming SSE)
- **Content-Type:** `text/event-stream`
- **Header:** `X-Conversation-Id: <uuid>`
- **Data frames:**
  - `data: {"choices":[{"delta":{"content":"..."}}]}`
  - `data: [DONE]`

### Example (Non-Streaming)
```bash
curl http://<pi-ip>:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

---

## 2) POST `/v1/audio/speech`

### Purpose
Text-to-speech (TTS). Accepts OpenAI-style fields and returns audio bytes in `opus`, `mp3`, or `pcm`. Unsupported
formats return a 400 error.

### Request (JSON)
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `input` | string | **Yes** | Text to speak. It is sanitized before synthesis. If empty, the synthesized output will be empty/silent. |
| `format` | string | No | Audio format. Valid values: `opus`, `mp3`, `pcm`. Defaults to server config (`cfg.tts.default_format`). Unsupported values return 400. |
| `model` | string | No | Accepted for compatibility but unused by Piper backend. |
| `voice` | string | No | Accepted for compatibility but unused by Piper backend. |

### Response
- **Status:** 200
- **Body:** Binary audio bytes
- **Headers:** `Content-Type` and `Content-Length` based on selected format:
  - `opus` → `audio/ogg`
  - `mp3` → `audio/mpeg`
  - `pcm` → `application/octet-stream`

### Error Responses
- `400` for unsupported format.
- `499` with `{"error":"client disconnected"}` if the client disconnects mid-generation.

### Example
```bash
curl http://<pi-ip>:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello from Pi AI Stack!",
    "format": "mp3"
  }' \
  --output speech.mp3
```

---

## 3) POST `/v1/audio/transcriptions`

### Purpose
Speech-to-text (STT). Accepts audio file upload and returns a JSON transcription.

### Request (multipart/form-data)
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `file` | file | **Yes** | Audio file to transcribe. Read fully into memory before transcription. |
| `model` | string | No | Defaults to `"whisper-1"`. Present for OpenAI compatibility (currently not used to select model). |
| `language` | string | No | Language hint. If omitted, uses server default `cfg.stt.language` for Whisper transcription. |

### Response (JSON)
```json
{ "text": "<transcription>" }
```

### Example
```bash
curl http://<pi-ip>:8000/v1/audio/transcriptions \
  -F "file=@/path/to/audio.wav" \
  -F "language=en"
```

---

## 4) POST `/internal/gc/run` (Internal)

### Purpose
Manually trigger garbage collection for conversations, knowledge entries, and RAG chunks. Returns a structured summary
of what was expired/deleted and whether storage limits were enforced.

### Request
No body required.

### Response (JSON)
Shape (example fields):
```json
{
  "ts": "<iso8601>",
  "results": {
    "expired_conversations": <int>,
    "deleted_conversations": <int>,
    "deleted_expired_knowledge": <int>,
    "deleted_expired_rag": <int>,
    "limits": {
      "limit_triggered": <bool>,
      "steps": [ ... ],
      "final_db_size_mb": <float>,
      "final_rag_entries": <int>
    }
  }
}
```

---

## 5) GET `/internal/gc/last` (Internal)

### Purpose
Retrieve the last GC run result or indicate that no GC has been run yet.

### Response
- If GC has run: returns the same object as `/internal/gc/run`.
- If not: `{"status":"no_gc_run_yet"}`.

---

## 6) POST `/internal/rag/ingest` (Internal)

### Purpose
Ingest a document into the RAG store. Inserts chunked text and embeddings into the `rag_chunks` table.

### Request (JSON)
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `text` | string | **Yes** | Text to chunk, embed, and store. Empty text is rejected by the ingest pipeline. |
| `doc_id` | string | No | Optional document ID; if omitted a UUID is generated. |
| `confidence` | number | No | Defaults to `0.95`. Must be ≥ `cfg.rag.persistence.min_confidence` and > 0.0, otherwise rejected. |
| `source` | string | No | Defaults to `"user_ingest"`; stored with each chunk for provenance. |
| `metadata` | object | No | Arbitrary metadata stored as JSON alongside chunks. |

### Response
- **Success:**
  ```json
  { "accepted": true, "doc_id": "<id>", "chunks": <int> }
  ```
- **Possible rejections:**
  - `{ "accepted": false, "reason": "rag_disabled" }`
  - `{ "accepted": false, "reason": "rag_persistence_disabled" }`
  - `{ "accepted": false, "reason": "confidence_below_threshold" }`
  - `{ "accepted": false, "reason": "low_confidence" }`
  - `{ "accepted": false, "reason": "empty" }`

---

## 7) GET `/metrics` (Optional)

### Purpose
Expose lightweight JSON metrics (counters and timers). This router is only registered if observability is enabled in
configuration.

### Response (JSON)
```json
{
  "counters": { "<name>": <int>, ... },
  "timers": {
    "<name>": { "count": <int>, "min_ms": <float>, "max_ms": <float>, "avg_ms": <float> },
    ...
  }
}
```

### Availability
Only mounted when `cfg.observability.enabled` is true.
