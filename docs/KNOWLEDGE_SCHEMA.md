# KNOWLEDGE SCHEMA – Pi AI Stack

This document defines the **data schema** used by the RAG (Retrieval-Augmented Generation) and memory subsystems in the Pi AI Stack.

It complements `KNOWLEDGE_POLICIES.md` by specifying **how governed knowledge is physically stored**, indexed, and aged.

---

## 1. Design Goals

The schema is designed to:

* support confidence-gated knowledge persistence
* represent time validity explicitly
* distinguish static, semi-static, and dynamic knowledge
* support efficient retrieval on constrained hardware
* age and clean data safely

SQLite is used as the storage backend.

---

## 2. Knowledge Categories (Recap)

Each knowledge entry is classified as one of:

* `static`
* `semi_static`
* `dynamic`

Dynamic knowledge is **not persisted by default**.

---

## 3. Table: `knowledge_entries`

This table stores persisted factual knowledge.

```sql
CREATE TABLE knowledge_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,

  content TEXT NOT NULL,              -- canonical fact text
  embedding BLOB,                     -- vector embedding (optional)

  category TEXT NOT NULL,             -- 'static' | 'semi_static'

  confidence REAL NOT NULL,           -- 0.0 – 1.0

  source TEXT NOT NULL,               -- 'assistant_local' | 'assistant_fallback_openai' | 'user_explicit'

  valid_from DATETIME NOT NULL,
  valid_to DATETIME,                  -- NULL for static knowledge

  created_at DATETIME NOT NULL,
  last_verified_at DATETIME,

  metadata_json TEXT                  -- optional non-semantic metadata
);
```

---

## 4. Indices

Efficient retrieval and cleanup rely on the following indices:

```sql
CREATE INDEX idx_knowledge_category
  ON knowledge_entries (category);

CREATE INDEX idx_knowledge_confidence
  ON knowledge_entries (confidence);

CREATE INDEX idx_knowledge_validity
  ON knowledge_entries (valid_from, valid_to);

CREATE INDEX idx_knowledge_source
  ON knowledge_entries (source);
```

---

## 5. Embeddings

### Storage

* Embeddings are stored as a BLOB
* Format depends on the embedding backend
* Size is kept minimal for Raspberry Pi constraints

### Semantics

* Embeddings are **never generated blindly**
* Embeddings are created **only after** a knowledge entry passes policy checks
* Failed or rejected knowledge has no embedding

---

## 6. Validity Semantics

### Static Knowledge

* `valid_to` is NULL
* assumed valid indefinitely
* may still be invalidated manually or by policy

### Semi-Static Knowledge

* `valid_to` is required
* retrieval checks current time against validity window

Expired entries are ignored during retrieval.

---

## 7. Confidence & Source Interaction

Rules enforced at schema level:

* `confidence` must be ≥ policy threshold
* fallback-derived entries require higher confidence
* user-explicit facts must be unambiguous

Entries failing checks are never inserted.

---

## 8. Metadata (`metadata_json`)

Optional metadata may include:

* extraction method
* model identifier
* scoring version
* revalidation notes

Rules:

* metadata is never used for retrieval
* metadata is never injected into prompts

---

## 9. Relationship to Conversations

Knowledge entries are **not tightly coupled** to conversations.

Optionally, an auxiliary table may track provenance:

```sql
CREATE TABLE knowledge_provenance (
  knowledge_id INTEGER NOT NULL,
  conversation_id TEXT,
  message_id INTEGER,
  created_at DATETIME NOT NULL,

  FOREIGN KEY (knowledge_id) REFERENCES knowledge_entries(id)
);
```

This table is optional and not required for retrieval.

---

## 10. Cleanup & Aging Support

The schema supports cleanup operations:

* delete expired `semi_static` entries
* delete low-confidence entries if policies tighten
* rebuild embeddings if model changes

Cleanup may be:

* lazy (on access)
* periodic (background job)

---

## 11. Explicit Non-Goals

This schema does **not** support:

* automatic self-training
* gradient updates
* online learning

It is a governed memory store only.

---

## 12. Summary

The Pi AI Stack knowledge schema:

* makes time and confidence first-class
* prevents uncontrolled knowledge growth
* supports reliable long-term behavior
* aligns strictly with `KNOWLEDGE_POLICIES.md`

It provides a solid foundation for RAG on constrained hardware.
