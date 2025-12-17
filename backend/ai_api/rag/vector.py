from __future__ import annotations
import math, struct
from typing import List

def to_f32_blob(vec: List[float]) -> bytes:
    return struct.pack("<" + "f"*len(vec), *vec)

def from_f32_blob(blob: bytes, dim: int) -> List[float]:
    return list(struct.unpack("<" + "f"*dim, blob))

def l2_norm(vec: List[float]) -> float:
    return math.sqrt(sum(x*x for x in vec)) or 1.0

def cosine_sim(a: List[float], b: List[float], norm_a: float, norm_b: float) -> float:
    return sum(x*y for x,y in zip(a,b)) / (norm_a * norm_b)
