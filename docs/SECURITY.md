# SECURITY – Pi AI Stack

This document describes the **security model and guarantees** of the Pi AI Stack.

The Pi AI Stack is designed to run primarily in **trusted local networks** and on **single-user devices** (e.g. Raspberry Pi).
Security decisions are therefore explicit, conservative, and easy to reason about.

---

## 1. Security Philosophy

The security model follows these core principles:

* **Local-first trust**: the system assumes a trusted LAN by default
* **Explicit exposure**: nothing is exposed unless intentionally configured
* **Least privilege**: services run with minimal permissions
* **No silent data exfiltration**: no telemetry, no phone-home
* **Predictable behavior**: no hidden background learning or syncing

Security is designed to be understandable rather than opaque.

---

## 2. Network Exposure Model

### Default Behavior

By default:

* FastAPI **binds to `127.0.0.1` only**
* Ollama **binds to localhost**
* Whisper and Piper are local-only processes
* **Nginx is the only service exposed to the LAN**

This ensures a single, controllable ingress point.

---

### Nginx as Security Boundary

Nginx acts as:

* reverse proxy
* network boundary
* protocol terminator

Responsibilities:

* expose `/v1/*` API endpoints
* disable buffering for streaming endpoints
* optionally enforce access control

FastAPI and internal services are never directly reachable from the network.

---

## 3. Authentication & Authorization

### Current State (v1)

* **No authentication is enabled by default**
* Any device on the local network can access the API

This is intentional and aligned with the local-assistant use case.

---

### When Authentication Is Required

Authentication **must** be added if:

* the API is exposed beyond a trusted LAN
* the device is multi-user
* the assistant controls sensitive resources

Possible future mechanisms:

* HTTP Basic Auth via Nginx
* token-based auth (API keys)
* mTLS

These are explicitly **out of scope for v1**.

---

## 4. Transport Security (TLS)

### Default

* HTTP only
* no TLS

This is acceptable for trusted LANs.

---

### When TLS Is Required

TLS **must** be enabled if:

* traffic crosses untrusted networks
* Wi-Fi security is weak or unknown
* the API is exposed to the internet

TLS termination should be handled by **Nginx**.

---

## 5. Data Security & Privacy

### Stored Data

The system stores:

* conversation metadata
* user and assistant messages
* optional RAG knowledge

Stored locally in SQLite under `/opt/pi-ai-stack/data/`.

---

### Data Explicitly NOT Stored

The system never stores:

* raw audio input
* audio output
* user credentials
* prompts injected internally
* embeddings outside RAG storage

This is a **hard guarantee**.

---

## 6. Cancellation & Abuse Protection

Client-initiated cancellation:

* immediately stops LLM generation
* does not trigger retries
* does not trigger fallback

This prevents:

* resource exhaustion
* accidental token usage on fallback providers

Cancellation is treated as a control-flow event, not as an error.

---

## 7. OpenAI Fallback Security

If OpenAI fallback is enabled:

* it is **explicitly opt-in** via `config.yaml`
* API keys are stored locally only
* fallback is never triggered on cancellation

Users remain in full control of when external APIs are contacted.

---

## 8. RAG & Knowledge Integrity

To protect long-term knowledge integrity:

* only high-confidence information is persisted
* time-sensitive facts are classified separately
* low-confidence or outdated data is rejected

There is **no automatic self-training**.

RAG aging and cleanup policies prevent knowledge contamination.

---

## 9. File System & Permissions

Installation layout:

```
/opt/pi-ai-stack/
```

Security characteristics:

* owned by `root:root`
* services run with least required privileges
* no writable system paths outside `/opt/pi-ai-stack`

---

## 10. Denial-of-Service Considerations

The system is designed to mitigate accidental DoS:

* request cancellation is cheap
* streaming stops immediately on disconnect
* long-running generations have timeouts

Intentional DoS protection (rate limiting, auth) is out of scope for v1.

---

## 11. Threat Model (Explicitly Out of Scope)

The following are **not** protected against in v1:

* malicious LAN users
* physical access attacks
* kernel-level exploits
* side-channel attacks

These require additional layers not appropriate for a lightweight local assistant.

---

## 12. Summary

The Pi AI Stack security model provides:

* a clear network boundary
* strong local privacy guarantees
* no hidden data exfiltration
* explicit opt-in for external services

The system is secure **by default for local use**, and intentionally minimal in complexity.
