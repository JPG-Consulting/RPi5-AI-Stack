from __future__ import annotations
from ai_api.facts.types import FactCandidate

HIGH = 0.95
MID = 0.70
LOW = 0.40
ZERO = 0.0

STATIC_KEYS = {"name", "full_name", "birth_date"}
SEMI_KEYS = {"city", "country", "job", "company", "language", "timezone"}

def score_l1(f: FactCandidate) -> float:
    if f.fact_type == "dynamic":
        return ZERO
    if not f.object or len(f.object.strip()) < 2:
        return ZERO
    if f.predicate in STATIC_KEYS and f.fact_type == "static":
        return HIGH
    if f.predicate in SEMI_KEYS and f.fact_type == "semi_static":
        return MID
    return LOW
