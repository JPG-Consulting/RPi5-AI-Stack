from __future__ import annotations
from dataclasses import dataclass
from typing import List
import requests

@dataclass
class EmbeddingConfig:
    base_url: str
    model: str
    timeout_seconds: int = 120

class OllamaEmbeddings:
    def __init__(self, cfg: EmbeddingConfig):
        self.cfg = cfg

    def embed(self, text: str) -> List[float]:
        url = f"{self.cfg.base_url.rstrip('/')}/api/embeddings"
        r = requests.post(url, json={"model": self.cfg.model, "prompt": text}, timeout=self.cfg.timeout_seconds)
        r.raise_for_status()
        emb = r.json().get("embedding")
        if not isinstance(emb, list) or not emb:
            raise RuntimeError("Missing embedding")            
        return [float(x) for x in emb]
