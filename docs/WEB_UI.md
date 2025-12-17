# WEB UI – Pi AI Stack

This document describes the **optional Web UI** included with the Pi AI Stack.

The Web UI provides a **ChatGPT-like interface** built on top of the local, OpenAI-compatible API.

---

## 1. Purpose & Scope

The Web UI is designed to:

* provide an immediate, user-friendly interface
* demonstrate correct API usage
* validate streaming behavior (text + audio)
* serve as a reference client implementation

The Web UI is **not required** to use the Pi AI Stack.

---

## 2. High-Level Architecture

```
Browser
  ↓
Web UI (HTML / JS / CSS)
  ↓
Nginx
  ↓
/v1 OpenAI-compatible API
```

The Web UI:

* does not bypass Nginx
* uses the same endpoints as any external client
* contains no backend logic

---

## 3. Installation

The Web UI is **optional** and disabled by default.

To install it during setup:

```bash
INSTALL_WEB_UI=true curl -fsSL https://<repo-url>/install.sh | sudo bash
```

After installation, it is served automatically by Nginx.

---

## 4. Features

### 4.1 Chat Interface

* ChatGPT-style message layout
* Conversation history per session
* Automatic reuse of `conversation_id`

---

### 4.2 Streaming Text

* Uses Server-Sent Events (SSE)
* Tokens appear incrementally
* UI updates in real time

If the user starts typing:

* the active stream is cancelled
* backend generation stops immediately

---

### 4.3 Streaming Audio (TTS)

The Web UI supports real-time audio playback.

Supported formats:

* **OPUS** (default, low latency)
* MP3 (fallback)

Audio behavior:

* audio starts playing as soon as data arrives
* playback can be interrupted at any time
* interruption triggers request cancellation

---

### 4.4 Audio Interruption

If the user:

* starts typing
* sends a new message
* presses stop

Then:

* current audio playback stops immediately
* the underlying API request is cancelled

This prevents overlapping speech and wasted computation.

---

## 5. Speech-to-Text (STT)

The Web UI may optionally support voice input.

Behavior:

* audio is captured locally in the browser
* audio chunks may be shown as partial results (UI only)
* the API call uses **batch STT**

The UI does not expose true streaming STT.

---

## 6. Conversation Semantics

The Web UI respects backend conversation rules:

* conversations are identified by `conversation_id`
* expired conversations start fresh
* control commands ("repeat", "what were we talking about") do not pollute history

---

## 7. Error Handling

The Web UI handles:

* network errors
* backend errors
* cancellations

Client-initiated cancellation:

* is not shown as an error
* results in a clean UI state

---

## 8. Security Considerations

* the Web UI runs entirely in the browser
* no credentials are stored
* no user data is persisted client-side beyond session state

Security is enforced server-side via Nginx.

---

## 9. Limitations

The Web UI is intentionally minimal:

* no authentication UI
* no user management
* no admin controls
* no RAG inspection tools

Advanced features are out of scope.

---

## 10. Non-Goals

The Web UI is **not** intended to:

* replace the API
* provide enterprise features
* handle untrusted internet exposure

It is a reference and convenience interface only.

---

## 11. Summary

The Pi AI Stack Web UI:

* offers a simple ChatGPT-like experience
* validates streaming and cancellation behavior
* demonstrates correct API usage

It is optional, lightweight, and intentionally limited in scope.
