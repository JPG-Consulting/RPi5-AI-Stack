# Pi AI Stack

Pi AI Stack is a **local-first AI runtime** designed to run on **Raspberry Pi 5**.

It provides an **OpenAI-compatible API**, local speech capabilities, governed memory (RAG + Facts),
and an optional Web UI — all running locally without requiring cloud services.

The system is designed to be **robust, predictable, and easy to operate**.

---

## Features

- **OpenAI-compatible REST API**
- **Local LLM inference** via Ollama
- **Speech-to-Text (STT)** using Whisper
- **Text-to-Speech (TTS)** using Piper (streaming OPUS / MP3 / PCM)
- **Conversation memory** with context control
- **RAG pipeline** with governance and confidence thresholds
- **Facts extraction** with validation
- **Streaming responses** (text and audio)
- **Optional Web UI** (ChatGPT-like)
- **Offline-first** operation
- **systemd-based service**

---

## Architecture

Pi AI Stack is composed of:

- Nginx (optional reverse proxy + Web UI)
- FastAPI backend (single service)
- Local inference engines (Ollama, Whisper, Piper)
- SQLite storage

The backend owns **all intelligence and policy**.
Clients (including the Web UI) are thin and stateless.

For a complete architectural overview, see:

```
docs/ARCHITECTURE.md
```

---

## Installation

Installation is fully automated and installs Pi AI Stack as a systemd service.

```bash
git clone https://github.com/JPG-Consulting/RPi5-AI-Stack.git
cd RPi5-AI-Stack
sudo ./install.sh
```

After installation, the API is available at:

```
http://localhost:8000
```

For full installation instructions, see:

```
docs/INSTALL.md
```

---

## API Usage

The API is compatible with OpenAI clients.

Example:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local",
    "messages": [
      {"role": "user", "content": "Hola"}
    ]
  }'
```

More examples are available in:

```
docs/API_CONSUMPTION.md
```

---

## Configuration

All configuration is defined in:

```
config.yaml
```

Changes require a service restart:

```bash
sudo systemctl restart pi-ai-stack
```

Configuration options are documented in:

```
docs/CONFIGURATION.md
```

---

## Web UI

An optional Web UI is included.

- Chat streaming
- STT via microphone
- TTS streaming with OPUS → MP3 fallback
- Immediate interruption on typing

If enabled, the UI is served via Nginx.

See:

```
docs/WEB_UI.md
```

---

## Documentation Index

All documentation is available under:

```
docs/
```

Key documents:

- `ARCHITECTURE.md` – system design
- `INSTALL.md` – installation guide
- `CONFIGURATION.md` – configuration reference
- `API_CONSUMPTION.md` – API usage examples
- `SECURITY.md` – security considerations
- `OBSERVABILITY.md` – metrics and observability
- `KNOWLEDGE_SCHEMA.md` – RAG & Facts schema
- `KNOWLEDGE_POLICIES.md` – governance rules
- `DEVELOPMENT.md` – development notes
- `TESTING.md` – test strategy
- `WEB_UI.md` – Web UI details

---

## Design Principles

- Local-first
- Deterministic behavior
- Explicit policies
- Bounded memory
- Minimal operational complexity

---

## License

See the `LICENSE` file for details.
