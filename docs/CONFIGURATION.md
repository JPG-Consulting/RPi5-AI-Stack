# Configuration Guide – Pi AI Stack

This document describes **all configuration options** available in the Pi AI Stack.

All configuration is centralized in a single file:

```
config.yaml
```

No critical behavior is hardcoded in the application.

---

## 1. General Principles

* Configuration is **explicit and declarative**
* Sensible defaults are provided
* All values are read at startup
* A restart is required after changing `config.yaml`

---

## 2. LLM Configuration

```yaml
llm:
  provider: ollama

  ollama:
    base_url: http://127.0.0.1:11434
    model: llama3.2:3b
    timeout_seconds: 3600
```

### Options

| Key                      | Description                                  |
| ------------------------ | -------------------------------------------- |
| `provider`               | LLM backend provider (`ollama`)              |
| `ollama.base_url`        | Base URL where Ollama API is reachable       |
| `ollama.model`           | Default model to use                         |
| `ollama.timeout_seconds` | Maximum time allowed for a single generation |

Notes:

* The Ollama endpoint is **never hardcoded**
* Ollama may run locally or remotely

---

## 3. Conversation Lifecycle

```yaml
conversation:
  ttl_hours: 24
```

### Options

| Key         | Description                                              |
| ----------- | -------------------------------------------------------- |
| `ttl_hours` | Conversation expires after this many hours of inactivity |

### Semantics

* TTL is evaluated from `last_activity_at`
* Expired conversations are never rehydrated
* A new conversation is created automatically when needed

Recommended range:

* Minimum: **1 hour**
* Maximum: **168 hours (7 days)**

---

## 4. Context Assembly

```yaml
context:
  last_n_turns: 12
  max_tokens_soft: 2048
  max_tokens_hard: 4096
```

### Options

| Key               | Description                                      |
| ----------------- | ------------------------------------------------ |
| `last_n_turns`    | Number of recent user/assistant turns to include |
| `max_tokens_soft` | Preferred maximum token budget                   |
| `max_tokens_hard` | Absolute token limit (never exceeded)            |

Notes:

* The ContextAssembler is token-aware
* Summaries are used when needed to stay within limits

---

## 5. Speech-to-Text (STT)

```yaml
stt:
  engine: whisper
  model: small
  language: es
```

### Options

| Key        | Description                                            |
| ---------- | ------------------------------------------------------ |
| `engine`   | STT engine (`whisper`)                                 |
| `model`    | Whisper model size (`tiny`, `base`, `small`, `medium`) |
| `language` | Expected language for transcription                    |

Notes:

* STT is **batch-only** at the API level
* UI may perform pseudo-streaming internally

---

## 6. Text-to-Speech (TTS)

```yaml
tts:
  engine: piper
  default_format: opus

  streaming:
    enabled: true
```

### Options

| Key                 | Description                                 |
| ------------------- | ------------------------------------------- |
| `engine`            | TTS engine (`piper`)                        |
| `default_format`    | Default audio format (`mp3`, `opus`, `pcm`) |
| `streaming.enabled` | Enable streaming audio responses            |

Notes:

* All formats are generated from raw PCM internally
* Audio is never persisted

---

## 7. Retrieval-Augmented Generation (RAG)

```yaml
rag:
  enabled: true

  persistence:
    min_confidence: 0.85

  classification:
    static_threshold: 0.9
    dynamic_threshold: 0.6
```

### Options

| Key                                | Description                                      |
| ---------------------------------- | ------------------------------------------------ |
| `enabled`                          | Enable or disable RAG entirely                   |
| `persistence.min_confidence`       | Minimum confidence required to persist knowledge |
| `classification.static_threshold`  | Confidence required to mark knowledge as static  |
| `classification.dynamic_threshold` | Threshold for semi-static knowledge              |

Semantics:

* Time-sensitive facts are treated differently from static knowledge
* Low-confidence data is never persisted

---

## 8. OpenAI Fallback

```yaml
fallback:
  openai:
    enabled: false
    api_key: null
```

### Options

| Key       | Description               |
| --------- | ------------------------- |
| `enabled` | Enable fallback to OpenAI |
| `api_key` | OpenAI API key            |

Rules:

* Fallback is **never** triggered on client cancellation
* Fallback is only used after scoring determines low confidence

---

## 9. Observability

```yaml
observability:
  enabled: true

  metrics:
    include_latency: true
    include_cancellations: true
```

### Options

| Key                             | Description                 |
| ------------------------------- | --------------------------- |
| `enabled`                       | Enable internal metrics     |
| `metrics.include_latency`       | Track latency per subsystem |
| `metrics.include_cancellations` | Track cancelled requests    |

Notes:

* Metrics are numeric only
* No user content is ever stored

---

## 10. Security & Exposure

```yaml
network:
  bind_address: 127.0.0.1
  exposed_via_nginx: true
```

Notes:

* FastAPI always binds to localhost
* Nginx is the only exposed service
* TLS and authentication are out of scope for v1

---

## 11. Configuration Summary

The Pi AI Stack configuration:

* centralizes all behavior in `config.yaml`
* avoids hardcoded values
* enables safe evolution of the system

Any change in configuration requires a service restart to take effect.
