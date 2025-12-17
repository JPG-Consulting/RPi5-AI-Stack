# Pi AI Stack – Documentation Index

This directory contains the **complete, authoritative specification** of Pi AI Stack.

The documentation is intentionally exhaustive and explicit so that:
- a developer can implement the project end-to-end
- an AI system (ChatGPT, Claude, Copilot) can regenerate or analyze the codebase
- architectural decisions remain stable over time

## Core

- ARCHITECTURE.md – One-page system architecture and data flow
- INSTALL.md – End-user installation guide
- CONFIGURATION.md – Full configuration reference
- API_CONSUMPTION.md – How to consume the OpenAI-compatible API
- WEB_UI.md – Optional Web UI architecture

## Knowledge, Memory & RAG

- KNOWLEDGE_POLICIES.md – Formal rules governing learning and persistence
- KNOWLEDGE_SCHEMA.md – SQLite schema for conversations, RAG, and facts
- RETENTION_AND_GC.md – Retention, TTLs, grace periods, and garbage collection

## Operations

- OBSERVABILITY.md – Metrics and operational visibility
- SECURITY.md – Security assumptions and hardening

## Development & Quality

- DEVELOPMENT.md – Developer workflow and conventions
- TESTING.md – Unit, cognitive, and golden tests
