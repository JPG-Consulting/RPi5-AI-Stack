# Retention and Garbage Collection

The system enforces bounded growth.

## Conversations

- TTL: configurable (default 24h)
- Grace period: configurable
- After TTL → expired
- After TTL + grace → deleted

## Knowledge

- Static facts: no expiry
- Semi-static facts: expiry
- Dynamic facts: never persisted

## Hard limits

- Max database size
- Max RAG entries

If limits are exceeded, low-confidence data is removed first.
