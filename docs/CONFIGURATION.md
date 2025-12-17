# Configuration

Pi AI Stack is configured via a single YAML file: `config.yaml`.

## Example

```yaml
llm:
  provider: ollama
  ollama:
    base_url: http://127.0.0.1:11434
    model: llama3.2:3b

stt:
  provider: whisper
  language: es

tts:
  provider: piper
  default_format: opus

facts:
  enabled: true
  min_confidence_persist: 0.85

rag:
  enabled: true
  embeddings:
    provider: ollama

conversation:
  ttl_hours: 24
  grace_period_hours: 12
```

All configuration options are explicit and documented inline.
No environment variables are required by default.
