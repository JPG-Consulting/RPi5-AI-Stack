from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel
import yaml

class OllamaCfg(BaseModel):
    base_url: str
    model: str
    timeout_seconds: int = 3600

class LlmCfg(BaseModel):
    provider: str = "ollama"
    ollama: OllamaCfg

class WhisperModelCfg(BaseModel):
    model: str = "small"

class SttCfg(BaseModel):
    engine: str = "whisper"
    language: str = "es"
    device: str = "cpu"
    compute_type: str = "int8"
    whisper: WhisperModelCfg = WhisperModelCfg()

class PiperCfg(BaseModel):
    binary: str = "/opt/pi-ai-stack/backend/.venv/bin/piper-tts"
    model: str

class TtsCfg(BaseModel):
    engine: str = "piper"
    default_format: str = "opus"
    sample_rate: int = 22050
    piper: PiperCfg

class ConversationCfg(BaseModel):
    ttl_hours: int = 24
    grace_period_hours: int = 72

class ContextCfg(BaseModel):
    last_n_turns: int = 12
    max_tokens_soft: int = 2048
    max_tokens_hard: int = 4096

class RagEmbOllamaCfg(BaseModel):
    base_url: str
    model: str
    timeout_seconds: int = 120

class RagEmbCfg(BaseModel):
    provider: str = "ollama"
    ollama: RagEmbOllamaCfg

class RagRetrievalCfg(BaseModel):
    top_k: int = 6
    min_similarity: float = 0.25

class RagPersistenceCfg(BaseModel):
    enabled: bool = True
    min_confidence: float = 0.85

class RagCfg(BaseModel):
    enabled: bool = True
    embeddings: RagEmbCfg
    retrieval: RagRetrievalCfg = RagRetrievalCfg()
    persistence: RagPersistenceCfg = RagPersistenceCfg()

class FactsL2OllamaCfg(BaseModel):
    base_url: str
    model: str
    timeout_seconds: int = 120

class FactsL2Cfg(BaseModel):
    enabled: bool = True
    provider: str = "ollama"
    ollama: FactsL2OllamaCfg

class FactsCfg(BaseModel):
    enabled: bool = True
    user_id: str = "default"
    min_confidence_persist: float = 0.85
    max_facts_in_prompt: int = 12
    l2: FactsL2Cfg

class StorageCfg(BaseModel):
    db_path: str = "/opt/pi-ai-stack/data/conversations.db"
    max_db_size_mb: int = 512
    max_rag_entries: int = 10000

class GcPeriodicCfg(BaseModel):
    enabled: bool = True
    interval_minutes: int = 60

class GcCfg(BaseModel):
    periodic: GcPeriodicCfg = GcPeriodicCfg()

class ObservabilityCfg(BaseModel):
    enabled: bool = True

class AppCfg(BaseModel):
    llm: LlmCfg
    stt: SttCfg = SttCfg()
    tts: TtsCfg
    conversation: ConversationCfg = ConversationCfg()
    context: ContextCfg = ContextCfg()
    rag: RagCfg
    facts: FactsCfg
    storage: StorageCfg = StorageCfg()
    gc: GcCfg = GcCfg()
    observability: ObservabilityCfg = ObservabilityCfg()

def load_config(path: str | Path | None = None) -> AppCfg:
    if path is None:
        # backend/ai_api/config.py → repo root
        path = Path(__file__).resolve().parents[2] / "config.yaml"

    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return AppCfg.model_validate(data)
