from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional

FactType = Literal["static", "semi_static", "dynamic"]

@dataclass
class FactCandidate:
    subject: str
    predicate: str
    object: str
    fact_type: FactType
    evidence: str
    confidence_l1: float = 0.0
    confidence_l2: Optional[float] = None

    def final_confidence(self) -> float:
        return self.confidence_l2 if self.confidence_l2 is not None else self.confidence_l1
