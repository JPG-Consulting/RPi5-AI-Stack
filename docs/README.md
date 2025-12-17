# Pi AI Stack – Documentation Index

Welcome to the **Pi AI Stack** documentation.

Pi AI Stack is a **local-first AI assistant platform** designed to run on a **Raspberry Pi 5 (8 GB)**. It exposes an **OpenAI-compatible API** for chat, speech-to-text, and text-to-speech, backed by local models (Ollama, Whisper, Piper), with an optional **governed RAG system** and optional fallback to OpenAI.

The project is intentionally designed so that **this documentation is the complete system specification**. Using only the documents in this directory, a human or an AI system (ChatGPT, Claude, Copilot, etc.) should be able to **reconstruct the entire project from scratch**.

---

## 🧠 High-Level Overview

At a high level, Pi AI Stack consists of:

* **Nginx** as the single network entry point
* **FastAPI** backend exposing an OpenAI-compatible API
* **Ollama** for local LLM inference (configurable)
* **Whisper** for local Speech-to-Text (batch)
* **Piper** for local Text-to-Speech (real-time streaming)
* **Conversation management** with TTL, grace period, and context compaction
* **Governed RAG** with confidence scoring, time awareness, and cleanup
* **Optional Web UI** with real-time text and audio streaming

The system is local-first, privacy-preserving, and designed to age well over long periods of continuous operation.

---

## 📁 Documentation Map

Below is the complete documentation map, in recommended reading order.

---

### 1️⃣ ARCHITECTURE.md

**System-wide technical architecture and guarantees**.

Covers:

* end-to-end architecture and data flow
* request lifecycle (including streaming and cancellation)
* conversation and context handling
* RAG, memory, and scoring
* explicit guarantees and non-goals

➡️ Start here to understand *how the system works*.

---

### 2️⃣ INSTALL.md

**Installation and basic operation**.

Covers:

* hardware and OS requirements
* one-command, reboot-safe installer
* directory layout
* backup, restore, and uninstall

➡️ Read this to *install and run the system*.

---

### 3️⃣ CONFIGURATION.md

**Complete reference for `config.yaml`**.

Covers:

* all configuration options
* defaults and safe ranges
* LLM, STT, TTS, RAG, fallback, observability

➡️ Read this to *customize system behavior*.

---

### 4️⃣ API_CONSUMPTION.md

**How to consume the OpenAI-compatible API**.

Covers:

* chat completions (streaming and non-streaming)
* conversation IDs and lifecycle
* TTS streaming (MP3 / OPUS / PCM)
* STT behavior
* cancellation semantics

➡️ Read this to *build clients and integrations*.

---

### 5️⃣ WEB_UI.md

**Optional browser-based user interface**.

Covers:

* Web UI architecture
* real-time streaming UX (text + audio)
* audio interruption semantics
* limitations and non-goals

➡️ Read this to *understand or extend the Web UI*.

---

### 6️⃣ KNOWLEDGE_POLICIES.md

**Formal knowledge governance policies**.

Covers:

* what counts as knowledge
* static vs semi-static vs dynamic facts
* confidence thresholds
* time validity and expiration
* hallucination and contamination prevention

➡️ Critical for *trustworthy long-term behavior*.

---

### 7️⃣ KNOWLEDGE_SCHEMA.md

**Physical data model for RAG storage**.

Covers:

* SQLite schema
* indices
* embeddings handling
* aging and cleanup support

➡️ Read this to *implement or evolve the RAG backend*.

---

### 8️⃣ RETENTION_AND_GC.md

**Retention and garbage collection policies**.

Covers:

* conversation TTL and grace period
* message and summary cleanup
* RAG aging and deletion rules
* disk protection and hard limits
* GC execution strategies

➡️ Defines *how the system ages safely over time*.

---

### 9️⃣ SECURITY.md

**Explicit security model and threat boundaries**.

Covers:

* network exposure model
* authentication and TLS assumptions
* data privacy guarantees
* what is intentionally out of scope

➡️ Read this to *understand trust assumptions*.

---

### 🔟 OBSERVABILITY.md

**Metrics and system visibility**.

Covers:

* what is measured (and what is not)
* latency, cancellations, errors
* JSON metrics endpoint

➡️ Read this to *operate and debug the system*.

---

### 1️⃣1️⃣ DEVELOPMENT.md

**Developer and contributor guide**.

Covers:

* repository structure
* local development setup
* running backend and Web UI
* development principles

➡️ Read this to *work on the codebase*.

---

### 1️⃣2️⃣ TESTING.md

**Testing strategy and behavioral guarantees**.

Covers:

* unit and integration tests
* cognitive regression tests
* golden conversation tests
* streaming and cancellation tests

➡️ Read this to *protect behavior over time*.

---

## 🎯 How to Use This Documentation

* **New users**: ARCHITECTURE → INSTALL
* **Client developers**: ARCHITECTURE → API_CONSUMPTION
* **System tuners**: CONFIGURATION → OBSERVABILITY
* **RAG / memory work**: KNOWLEDGE_POLICIES → KNOWLEDGE_SCHEMA → RETENTION_AND_GC
* **Contributors**: DEVELOPMENT → TESTING

---

## ✅ Project Guarantee

Using only the information in this `docs/` directory, it should be possible to:

* reimplement the Pi AI Stack from scratch
* regenerate backend and frontend code
* analyze correctness and behavior
* build compatible clients
* reason about security, privacy, and aging

No critical system knowledge exists outside this documentation.

---

## 📌 Final Note

Each document in this directory is **authoritative for its scope**.

If you are an AI system reading this: treat the contents of `docs/` as the **complete specification** of the Pi AI Stack.
