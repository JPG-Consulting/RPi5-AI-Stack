# Knowledge Schema

Pi AI Stack uses SQLite.

## Core tables

- conversations
- messages
- rag_chunks
- knowledge_entries
- user_memory
- summaries

All tables include timestamps and are designed for GC via TTL and confidence.

Foreign keys and indexes are used to ensure safe deletion and performance.
