# RETENTION AND GARBAGE COLLECTION (GC) – Pi AI Stack

This document defines the **formal retention and garbage collection policies** of the Pi AI Stack.

It is a **normative specification**: all rules described here must be enforced by the implementation.

The goal is to ensure that the system:

* ages well over time
* does not grow unbounded
* preserves cognitive quality
* remains predictable and operable on constrained hardware

---

## 1. Core Principles

All retention and GC behavior follows these principles:

1. Nothing is eternal by default
2. Expiration is explicit and time-based
3. Cleanup is safe, not aggressive
4. No data "in use" is ever removed
5. GC never changes system semantics

Garbage collection is about **healthy aging**, not reset or loss of meaning.

---

## 2. Data Classes

The Pi AI Stack handles the following data classes:

| Data type         | Persistent | Governed           |
| ----------------- | ---------- | ------------------ |
| Conversations     | Yes        | TTL + GC           |
| Messages          | Yes        | Conversation-bound |
| Context summaries | Yes        | Regenerable        |
| RAG / Knowledge   | Yes        | Policies + time    |
| User memory       | Yes        | TTL                |
| Metrics           | No         | In-memory only     |
| Audio             | No         | Never stored       |

GC applies only to **persistent data**.

---

## 3. Conversation Retention

### Configuration

```yaml
conversation:
  ttl_hours: 24
  grace_period_hours: 72
```

### Semantics

* `ttl_hours` defines inactivity before a conversation expires
* expiration is based on `last_activity_at`
* once expired, a conversation:

  * is never rehydrated
  * is never reused for context
  * may remain on disk temporarily

---

### Grace Period

`grace_period_hours` defines how long an **expired** conversation is kept on disk before physical deletion.

Purpose:

* debugging
* crash / reboot tolerance
* inspection and audits

Grace period **does not** extend conversational life.

---

### Deletion Rule

A conversation is permanently deleted when:

```
now - last_activity_at > ttl_hours + grace_period_hours
```

Deletion is atomic and removes:

* conversation record
* all messages
* all summaries

---

## 4. Message Retention

* messages have no independent TTL
* messages live and die with their conversation
* system messages are not exempt

There is no global message archive.

---

## 5. Context Summaries

Context summaries are:

* derived
* regenerable
* non-authoritative

Retention rules:

* deleted when conversation expires
* may be deleted earlier if context is recomputed

GC may remove summaries **before** messages if needed.

---

## 6. RAG / Knowledge Retention

RAG retention strictly follows `KNOWLEDGE_POLICIES.md`.

---

### 6.1 Static Knowledge

* no automatic TTL
* retained indefinitely by default
* removable by policy change or manual invalidation

---

### 6.2 Semi-Static Knowledge

* must include `valid_to`
* ignored after expiry
* automatically deleted by GC

---

### 6.3 Dynamic Knowledge

* not persisted
* never enters GC

---

## 7. User Memory Retention

User-specific memory follows conservative rules:

```yaml
user_memory:
  ttl_days: 30
```

Rules:

* scoped to user / conversation
* never generalized
* expires automatically

Expired user memory is removed by GC.

---

## 8. Storage Limits (Hard Guards)

To protect disk usage:

```yaml
storage:
  max_db_size_mb: 512
  max_rag_entries: 10000
```

### Behavior at Limits

1. Requests are never rejected
2. GC runs immediately
3. Deletion order:

   * expired conversations
   * expired semi-static knowledge
   * lowest-confidence entries
   * oldest entries

If limits are still exceeded:

* RAG persistence is temporarily disabled
* system continues serving requests

This is a **fail-safe degradation**, not failure.

---

## 9. GC Execution Strategy

GC uses two complementary strategies.

---

### 9.1 Lazy GC (Primary)

* executed during normal operations
* triggered on read/write paths
* amortized cost
* no background threads required

---

### 9.2 Periodic GC (Optional)

```yaml
gc:
  periodic:
    enabled: true
    interval_minutes: 60
```

* lightweight background task
* no external cron required
* safe on Raspberry Pi

---

## 10. Observability

GC exposes **metadata only**, never content:

* GC runs count
* GC duration
* conversations expired
* conversations deleted
* RAG entries deleted

All metrics are described in `OBSERVABILITY.md`.

---

## 11. Safety Guarantees

The retention system guarantees that:

* active conversations are never affected
* expired data is never reused
* RAG does not accumulate stale facts
* disk usage remains bounded

GC cannot change system answers or reasoning paths.

---

## 12. Non-Goals

Retention and GC do not aim to:

* archive historical conversations
* preserve data indefinitely
* act as backup mechanisms

Backups are explicitly handled separately.

---

## 13. Summary

The Pi AI Stack retention and GC model:

* enforces explicit data lifetimes
* prevents silent degradation
* protects constrained hardware
* ensures predictable long-term behavior

With these rules, the system can safely run **for months without manual intervention**.
