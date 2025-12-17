# KNOWLEDGE POLICIES – Pi AI Stack

This document defines the **formal policies governing knowledge persistence** in the Pi AI Stack.

It is a **normative document**: its rules are enforced in code and are designed to ensure that the system ages well, remains reliable, and avoids hallucination-driven contamination.

---

## 1. Core Principles

All knowledge persistence follows these principles:

* **No silent learning**: the system never learns implicitly
* **Explicit persistence**: every stored fact passes policy checks
* **Confidence-gated**: low-confidence information is rejected
* **Time-aware**: not all facts age the same
* **Reversible**: knowledge can expire or be invalidated

The RAG subsystem is not a training mechanism. It is a governed memory store.

---

## 2. What Counts as "Knowledge"

In the Pi AI Stack, *knowledge* refers to:

* factual statements extracted from assistant responses
* user-provided facts explicitly stated ("Me llamo Juan")
* structured information suitable for later retrieval

Knowledge does **not** include:

* opinions
* stylistic preferences
* ephemeral conversational context
* instructions or commands
* summaries used only for context compression

---

## 3. Knowledge Categories

All candidate knowledge is classified into one of the following categories:

### 3.1 Static Knowledge

Facts that are extremely unlikely to change.

Examples:

* "Paris is the capital of France"
* "Water freezes at 0°C"

Properties:

* long-lived
* rarely invalidated
* safe to reuse broadly

---

### 3.2 Semi-Static Knowledge

Facts that change infrequently, but **can** change.

Examples:

* "The president of Ukraine is X"
* "The CEO of company Y"

Properties:

* must include time context
* requires periodic revalidation
* expires faster than static knowledge

---

### 3.3 Dynamic Knowledge

Facts that are highly time-dependent.

Examples:

* weather
* stock prices
* current events

Properties:

* short-lived
* rarely persisted
* typically retrieved live or recomputed

Dynamic knowledge is **not persisted by default**.

---

## 4. Confidence Requirements

Knowledge persistence is gated by confidence scoring.

### Required Confidence Levels

* **Static knowledge**: ≥ 0.90
* **Semi-static knowledge**: ≥ 0.85
* **Dynamic knowledge**: not persisted

Confidence is derived from:

* model self-assessment
* secondary scoring (L2)
* grounding checks

If confidence is below threshold, the knowledge is rejected.

---

## 5. Time Awareness & Validity

Each persisted knowledge entry carries temporal metadata:

* `valid_from`
* optional `valid_to`

Rules:

* static knowledge may omit `valid_to`
* semi-static knowledge must include `valid_to`
* expired knowledge is ignored during retrieval

---

## 6. Source Attribution

Each knowledge entry records its origin:

* `assistant_local`
* `assistant_fallback_openai`
* `user_explicit`

Rules:

* fallback-derived knowledge requires higher confidence
* user-provided facts are only stored if explicit and unambiguous

---

## 7. Negative Persistence Rules (Critical)

The following information is **never persisted**:

* speculative answers
* guesses
* hedged statements ("maybe", "probably")
* answers with explicit uncertainty
* answers marked as outdated
* responses generated under fallback due to low confidence

This is a hard guarantee.

---

## 8. User Memory vs General Knowledge

User-specific facts ("My name is Juan") are treated separately:

* stored as **user memory**, not global knowledge
* scoped to the conversation or user identity
* never generalized

User memory follows the same confidence rules but different retrieval policies.

---

## 9. Retrieval Constraints

During retrieval:

* expired knowledge is ignored
* dynamic knowledge is excluded
* lower-confidence entries are deprioritized

Knowledge retrieval never overrides live computation when freshness matters.

---

## 10. Aging & Cleanup

Knowledge entries age according to category:

* static: very slow aging
* semi-static: moderate aging
* dynamic: immediate expiry

Aging policies are enforced during periodic cleanup and lazy evaluation.

---

## 11. Explicit Non-Goals

The RAG system is **not**:

* a self-training loop
* a truth oracle
* a replacement for live data sources

It exists to augment, not replace, reasoning.

---

## 12. Summary

These policies ensure that:

* the system remains trustworthy over time
* knowledge does not silently degrade
* hallucinations do not accumulate
* users retain control over what is remembered

Any knowledge stored in the Pi AI Stack is **explicitly governed, confidence-scored, and time-aware**.
