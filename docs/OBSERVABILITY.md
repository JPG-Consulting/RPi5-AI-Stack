# OBSERVABILITY – Pi AI Stack

This document describes how **observability** is implemented in the Pi AI Stack.

The goal of observability is to understand **system behavior and performance** without storing or exposing user content.

---

## 1. Observability Principles

Observability in the Pi AI Stack follows strict rules:

* **Privacy-first**: no user text, audio, or prompts are stored
* **Numeric-only**: metrics are numbers, counters, and timings
* **Local-only**: metrics are available locally via JSON
* **Low overhead**: suitable for Raspberry Pi hardware

There is no external telemetry or phone-home behavior.

---

## 2. What Is Observed

The system exposes metrics about:

* request volume
* latency
* cancellations
* errors
* resource usage (coarse)

Observability focuses on **how the system behaves**, not **what users say**.

---

## 3. Metrics Categories

### 3.1 Request Metrics

Tracked per endpoint:

* total requests
* active requests
* cancelled requests
* failed requests

Example:

```json
{
  "requests_total": 1240,
  "requests_active": 2,
  "requests_cancelled": 87,
  "requests_failed": 3
}
```

---

### 3.2 Latency Metrics

Latency is tracked for major pipeline stages:

* STT (Whisper)
* LLM generation (Ollama)
* TTS (Piper)
* end-to-end request time

Metrics are aggregated as:

* count
* average
* min / max

Example:

```json
{
  "llm_latency_ms": {
    "count": 1200,
    "avg": 1830,
    "min": 420,
    "max": 12400
  }
}
```

---

### 3.3 Cancellation Metrics

Client-initiated cancellations are explicitly tracked.

Important semantics:

* cancellation is **not an error**
* cancellation never triggers fallback

Metrics:

* cancellations per endpoint
* cancellations per minute

---

### 3.4 Error Metrics

Errors tracked include:

* backend exceptions
* upstream LLM errors
* STT / TTS failures

Errors caused by client cancellation are **not counted as failures**.

---

## 4. What Is NOT Observed

The following are **never** collected:

* user messages
* assistant responses
* audio input or output
* prompts (system or user)
* RAG contents
* embeddings

This is a hard guarantee.

---

## 5. Metrics Storage Model

* Metrics are kept **in memory only**
* No metrics are persisted to disk by default
* Metrics reset on service restart

This avoids:

* long-term accumulation
* privacy risks
* disk growth

---

## 6. Metrics Exposure

Metrics are exposed as **JSON** via an internal endpoint.

Example:

```
GET /internal/metrics
```

Characteristics:

* JSON only (no Prometheus)
* numeric fields only
* human-readable

This endpoint is:

* bound to localhost
* not exposed directly to the LAN

Nginx does not proxy this endpoint by default.

---

## 7. Relation to Other Components

### Conversation Control

Metrics include:

* number of repeat requests
* number of meta-summary requests

These metrics help understand UX patterns without storing content.

---

### RAG & Memory

Observability tracks:

* number of RAG retrievals
* number of persisted knowledge entries
* number of rejected (low-confidence) entries

No semantic content is exposed.

---

## 8. Performance Considerations

Observability is designed to be:

* lock-free where possible
* O(1) per update
* safe under high cancellation rates

The system must remain responsive even when many requests are aborted.

---

## 9. Extensibility

Future extensions may include:

* exporting metrics snapshots to disk
* optional Prometheus exporter
* integration with external dashboards

These features are **explicitly opt-in** and not enabled by default.

---

## 10. Summary

The Pi AI Stack observability model provides:

* insight into system health
* performance debugging tools
* strict privacy guarantees

It enables operators to understand and tune the system **without ever inspecting user data**.
