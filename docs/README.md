# Pi AI Stack – Documentation Index

Welcome to the **Pi AI Stack** documentation.

Pi AI Stack is a **local-first AI assistant platform** designed to run on a **Raspberry Pi 5 (8 GB)**. It provides an **OpenAI-compatible API** for chat, speech-to-text, and text-to-speech, backed by local models (Ollama, Whisper, Piper), with an optional governed RAG system and optional fallback to OpenAI.

The project is designed to be:

* local-first and privacy-preserving
* reproducible and inspectable
* safe against silent knowledge degradation
* suitable for long-running, stateful assistants

This documentation set is intentionally complete and explicit. An AI system (e.g. ChatGPT, Claude, Copilot) should be able to **reconstruct the entire project from scratch** using only these documents.

---

## 🧠 High-Level Overview

At a high level, Pi AI Stack consists of:

* **Nginx** as the single network entry point
* **FastAPI** backend exposing an OpenAI-compatible API
* **Ollama** for local LLM inference (configurable)
* **Whisper** for Speech-to-Text (local, batch)
* **Piper** for Text-to-Speech (local, streaming)
* **Conversation management** with TTL and context compaction
* **Governed RAG** with confidence, time-awareness, and cleanup
* **Optional Web UI** with real-time streaming UX

---

## 📁 Documentation Map

Below is an overview of all documentation files in this directory, in recommended reading order.

---

### 1️⃣ ARCHITECTURE.md

**System-wide technical vision and guarantees**.

Explains:

* overall architecture and data flow
* request lifecycle (including streaming and cancellation)
* conversation and context handling
* RAG, memory, and scoring concepts
* design guarantees and non-goals

➡️ Start here to understand *how the system works*.

---

### 2️⃣ INSTALL.md

**End-user installation guide**.

Explains:

* hardware and software requirements
* one-command installation
* reboot-safe installer behavior
* directory layout
* backup, restore, and uninstall

➡️ Read this to *install and run the system*.

---

### 3️⃣ CONFIGURATION.md

**Complete reference for `config.yaml`**.

Explains:

* all configuration options
* defaults and recommended ranges
* LLM, STT, TTS, RAG, fallback, observability

➡️ Read this to *tune and customize behavior*.

---

### 4️⃣ API_CONSUMPTION.md

**How to consume the API from clients**.

Explains:

* OpenAI-compatible chat API
* streaming chat (SSE)
* TTS streaming (MP3 / OPUS / PCM)
* STT behavior
* cancellation semantics
* real examples with `curl`

➡️ Read this to *build clients or integrations*.

---

### 5️⃣ WEB_UI.md

**Optional browser-based user interface**.

Explains:

* Web UI architecture
* streaming UX (text + audio)
* audio interruption semantics
* limitations and non-goals

➡️ Read this to *understand or extend the Web UI*.

---

### 6️⃣ KNOWLEDGE_POLICIES.md

**Formal policies governing RAG and memory**.

Explains:

* what counts as knowledge
* static vs semi-static vs dynamic facts
* confidence thresholds
* time validity and expiration
* rules preventing hallucination contamination

➡️ Critical for *trustworthy long-term behavior*.

---

### 7️⃣ KNOWLEDGE_SCHEMA.md

**Physical data model for RAG storage**.

Explains:

* SQLite schema
* indices
* embeddings handling
* aging and cleanup support

➡️ Read this to *implement or evolve the RAG backend*.

---

### 8️⃣ SECURITY.md

**Explicit security model and threat boundaries**.

Explains:

* network exposure model
* absence of auth by default (and why)
* TLS considerations
* data privacy guarantees
* what is intentionally out of scope

➡️ Read this to *understand trust assumptions*.

---

### 9️⃣ OBSERVABILITY.md

**Metrics and system visibility**.

Explains:

* what is measured (and what is not)
* latency, cancellations, errors
* JSON metrics endpoint
* privacy-preserving observability

➡️ Read this to *operate and debug the system*.

---

### 🔟 DEVELOPMENT.md

**Guide for developers and contributors**.

Explains:

* repository structure
* local dev setup
* running backend and Web UI
* configuration in dev
* coding principles

➡️ Read this to *work on the codebase*.

---

### 1️⃣1️⃣ TESTING.md

**Testing strategy and guarantees**.

Explains:

* unit vs integration tests
* cognitive regression tests
* golden conversation tests
* streaming and cancellation tests

➡️ Read this to *protect behavior over time*.

---

## 🎯 How to Use This Documentation

* **New users**: start with ARCHITECTURE → INSTALL
* **Client developers**: ARCHITECTURE → API_CONSUMPTION
* **System tuners**: CONFIGURATION → OBSERVABILITY
* **RAG / memory work**: KNOWLEDGE_POLICIES → KNOWLEDGE_SCHEMA
* **Contributors**: DEVELOPMENT → TESTING

---

## ✅ Project Guarantee

Using only the information in this `docs/` directory, it should be possible to:

* reimplement the Pi AI Stack from scratch
* regenerate backend and frontend code
* analyze correctness and behavior
* build compatible clients
* reason about security, privacy, and aging

No critical knowledge is hidden outside this documentation.

---

## 📌 Final Note

This index intentionally avoids low-level detail. Each linked document is authoritative for its scope.

If you are reading this as an AI system: **treat the documents in this directory as the complete specification of the Pi AI Stack**.
