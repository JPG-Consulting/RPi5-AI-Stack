# TESTING – Pi AI Stack

This document defines the **testing strategy** for the Pi AI Stack.

Testing is treated as a first-class concern, especially given the cognitive and stateful nature of the system.

---

## 1. Testing Principles

All tests follow these principles:

* determinism over randomness
* reproducibility
* no reliance on external services
* protection against behavioral drift

Tests are designed to detect **regressions in reasoning**, not just code errors.

---

## 2. Test Layers Overview

The test suite is organized into multiple layers:

1. Unit tests
2. Integration tests
3. Cognitive regression tests
4. Golden conversation tests

Each layer serves a distinct purpose.

---

## 3. Unit Tests

### Scope

Unit tests cover:

* pure functions
* policy evaluation logic
* scoring and classification
* context assembly logic

### Characteristics

* fast
* deterministic
* no I/O
* no database access

Example targets:

* KnowledgePolicy evaluation
* confidence threshold checks
* ConversationControl classification

---

## 4. Integration Tests

### Scope

Integration tests cover:

* API endpoints
* request / response contracts
* streaming behavior (protocol-level)
* database interactions

### Characteristics

* use a temporary SQLite database
* may start a real FastAPI app
* mock external dependencies

External APIs (OpenAI) are always stubbed.

---

## 5. Cognitive Regression Tests

### Purpose

Cognitive regression tests ensure that the **behavior of the system does not degrade** over time.

They are essential for:

* long-lived conversations
* context summarization
* RAG aging behavior
* memory extraction correctness

---

### Structure

A cognitive regression test:

* replays a full conversation
* captures structured outputs
* compares them against expectations

The comparison is **semantic**, not textual.

---

### What Is Compared

Examples:

* confidence scores
* classification results (static / semi-static)
* number of RAG insertions
* number of rejected facts
* summary length and token counts

---

## 6. Golden Conversation Tests

### Purpose

Golden tests protect against **unintentional behavior changes**.

They store:

* full conversations
* expected assistant outputs
* expected side effects (RAG writes, summaries)

---

### Rules

* golden files are versioned
* changes must be intentional
* reviewers must approve semantic differences

Golden tests are the last line of defense.

---

## 7. Streaming Tests

Streaming behavior must be tested explicitly:

* SSE token streaming
* audio chunk streaming
* cancellation mid-stream

Assertions include:

* stream stops on client disconnect
* no fallback triggered on cancellation
* no partial persistence

---

## 8. Cancellation Tests

Special tests validate cancellation semantics:

* cancelling chat streaming
* cancelling TTS streaming
* cancelling Web UI playback

Expected behavior:

* immediate stop
* clean state
* no errors recorded

---

## 9. RAG-Specific Tests

RAG tests validate:

* confidence gating
* time-awareness
* rejection of dynamic knowledge
* aging and cleanup behavior

Tests include scenarios such as:

* "Who is the president of X?"
* "What is the weather today?"

---

## 10. Performance & Load Tests

Given Raspberry Pi constraints:

* tests focus on stability, not throughput
* sustained operation under cancellations is tested

No stress testing beyond realistic local usage is required.

---

## 11. Mocking & Stubbing

Rules:

* Ollama may be mocked for speed
* OpenAI fallback is always stubbed
* STT / TTS engines may be replaced with fakes

Tests must never consume external resources.

---

## 12. Test Data Management

* test data lives under `tests/fixtures/`
* golden data is versioned
* large audio files are avoided

---

## 13. CI Considerations

Tests are designed to:

* run on modest hardware
* avoid GPU requirements
* complete in reasonable time

CI pipelines must not require Ollama or OpenAI.

---

## 14. Non-Goals

Testing does **not** aim to:

* validate model intelligence
* compare models competitively
* benchmark absolute quality

The goal is **consistency**, not intelligence ranking.

---

## 15. Summary

The Pi AI Stack testing strategy:

* protects cognitive behavior
* prevents silent regressions
* enforces system guarantees

Testing ensures the system remains reliable as it evolves.
