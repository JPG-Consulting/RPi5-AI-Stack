# Knowledge Policies

This document defines **hard rules** governing what the system is allowed to learn and persist.

## Core principles

- The system MUST NOT learn implicitly
- The system MUST NOT persist low-confidence information
- The system MUST NOT mix embedding providers

## Embedding provider policy

- Exactly one embedding provider is active at any time
- No automatic fallback between embedding providers
- Changing provider requires full re-embedding

## Facts

- Only explicit user statements may become facts
- Dynamic facts are never persisted
- Facts require confidence scoring (L1 + L2)

## RAG

- RAG entries must be:
  - non-dynamic
  - high confidence
  - time-aware

These rules exist to prevent silent corruption and hallucinated memory.
