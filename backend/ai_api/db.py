from __future__ import annotations
import sqlite3
from pathlib import Path
from contextlib import contextmanager

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  last_activity_at TEXT NOT NULL,
  status TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_conversations_activity
  ON conversations (last_activity_at);

CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL,
  meta_json TEXT,
  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_time
  ON messages (conversation_id, created_at);

CREATE TABLE IF NOT EXISTS summaries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_summaries_conversation
  ON summaries (conversation_id);

CREATE TABLE IF NOT EXISTS user_memory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  key TEXT NOT NULL,
  value TEXT NOT NULL,
  confidence REAL NOT NULL,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  metadata_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_user_memory_expires
  ON user_memory (expires_at);

CREATE TABLE IF NOT EXISTS knowledge_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  subject TEXT NOT NULL,
  predicate TEXT NOT NULL,
  object TEXT NOT NULL,
  fact_type TEXT NOT NULL,
  confidence REAL NOT NULL,
  valid_from TEXT NOT NULL,
  valid_to TEXT,
  source TEXT NOT NULL,
  created_at TEXT NOT NULL,
  metadata_json TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_knowledge_user_predicate
  ON knowledge_entries (subject, predicate);

CREATE INDEX IF NOT EXISTS idx_knowledge_valid_to
  ON knowledge_entries (valid_to);

CREATE TABLE IF NOT EXISTS rag_chunks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doc_id TEXT NOT NULL,
  chunk_index INTEGER NOT NULL,
  text TEXT NOT NULL,
  embedding BLOB NOT NULL,
  embedding_dim INTEGER NOT NULL,
  embedding_norm REAL NOT NULL,
  created_at TEXT NOT NULL,
  valid_from TEXT NOT NULL,
  valid_to TEXT,
  confidence REAL NOT NULL,
  source TEXT NOT NULL,
  metadata_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_rag_doc_chunk
  ON rag_chunks (doc_id, chunk_index);

CREATE INDEX IF NOT EXISTS idx_rag_validity
  ON rag_chunks (valid_from, valid_to);

CREATE INDEX IF NOT EXISTS idx_rag_confidence
  ON rag_chunks (confidence);
"""

def open_db(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA_SQL)
    return con

@contextmanager
def tx(con: sqlite3.Connection):
    cur = con.cursor()
    try:
        yield cur
        con.commit()
    except:
        con.rollback()
        raise
