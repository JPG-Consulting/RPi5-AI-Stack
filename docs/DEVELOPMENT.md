# DEVELOPMENT – Pi AI Stack

This document describes how to **develop, run, and test** the Pi AI Stack locally.

It is intended for contributors and maintainers working on the codebase.

---

## 1. Development Principles

Development follows these principles:

* local-first execution
* reproducibility
* explicit configuration
* no hidden dependencies
* fast feedback loops

The development environment should behave as closely as possible to production.

---

## 2. Repository Structure

```
pi-ai-stack/
├── backend/
│   └── ai_api/
│       ├── main.py
│       ├── routers/
│       ├── services/
│       ├── policies/
│       └── utils/
├── frontend/
│   └── web-ui/
├── docs/
├── nginx/
├── install.sh
├── config.yaml
└── tests/
```

---

## 3. Local Development Environment

### Requirements

* Linux or macOS
* Python 3.10+
* Node.js 18+ (for Web UI)
* Ollama installed locally

Docker is **not required**.

---

### Python Virtual Environment

Create and activate a virtual environment:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 4. Running the Backend

Start the API server locally:

```bash
uvicorn ai_api.main:app --reload --host 127.0.0.1 --port 8000
```

Notes:

* the API binds to localhost
* streaming endpoints work in development

---

## 5. Ollama in Development

Ollama must be running:

```bash
ollama serve
```

Pull the configured model:

```bash
ollama pull llama3.2:3b
```

The Ollama endpoint is configurable via `config.yaml`.

---

## 6. Web UI Development

Navigate to the Web UI directory:

```bash
cd frontend/web-ui
npm install
npm run dev
```

The Web UI:

* consumes the same OpenAI-compatible API
* supports streaming chat and audio
* runs independently from the backend

---

## 7. Configuration in Development

Development uses the same `config.yaml` as production.

Common adjustments:

* reduce model size
* lower context limits
* disable OpenAI fallback

Changes require restarting the backend.

---

## 8. Testing Strategy

The project uses multiple test layers:

* unit tests (pure logic)
* integration tests (API level)
* **cognitive regression tests**
* golden conversation tests

Tests live under:

```
tests/
```

---

## 9. Cognitive Regression Tests

Cognitive regression tests ensure that:

* answers do not degrade over time
* RAG does not contaminate itself
* summaries remain coherent

These tests replay full conversations and compare structured outputs.

---

## 10. Golden Tests

Golden tests store expected outputs for complete conversations.

Rules:

* golden data is versioned
* changes must be intentional
* reviewers must validate semantic changes

Golden tests protect against accidental behavior drift.

---

## 11. Mocking & Stubbing

For fast tests:

* Ollama can be mocked
* OpenAI fallback must always be stubbed

No tests should consume external API tokens.

---

## 12. Debugging & Observability

During development:

* enable verbose logging
* inspect `/internal/metrics`
* monitor cancellation metrics

User content must never be logged.

---

## 13. Code Style & Quality

* follow PEP8 for Python
* prefer explicit over implicit logic
* avoid large monolithic functions

Readability is prioritized over cleverness.

---

## 14. Non-Goals

Development does **not** aim to:

* optimize prematurely
* introduce hidden magic
* diverge dev and prod behavior

---

## 15. Summary

The Pi AI Stack development workflow:

* mirrors production closely
* supports safe iteration
* protects long-term system behavior

All contributors are expected to follow these guidelines.
