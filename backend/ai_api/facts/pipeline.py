from __future__ import annotations
from typing import Callable, List
from ai_api.facts.types import FactCandidate
from ai_api.facts.l1_rules import score_l1
from ai_api.facts.store import upsert_knowledge_entry

def run_facts_pipeline(con, cfg, user_subject: str, user_text: str, extractor_fn: Callable[[], List[FactCandidate]], l2_fn: Callable[[str,str,str], float]):
    if not cfg.facts.enabled:
        return {"enabled": False}

    cands = extractor_fn()
    accepted = rejected = 0

    for f in cands:
        f.confidence_l1 = score_l1(f)
        if f.confidence_l1 <= 0.0 or f.fact_type == "dynamic":
            rejected += 1
            continue

        if cfg.facts.l2.enabled and f.confidence_l1 < cfg.facts.min_confidence_persist:
            fact_str = f"{f.subject} {f.predicate} = {f.object}"
            f.confidence_l2 = l2_fn(fact_str, f.fact_type, f.evidence)

        final = f.final_confidence()
        if final >= cfg.facts.min_confidence_persist:
            upsert_knowledge_entry(
                con=con,
                subject=f.subject,
                predicate=f.predicate,
                object_=f.object,
                fact_type=f.fact_type,
                confidence=final,
                source="user_explicit",
                metadata={"evidence": f.evidence, "confidence_l1": f.confidence_l1, "confidence_l2": f.confidence_l2},
            )
            accepted += 1
        else:
            rejected += 1

    return {"enabled": True, "candidates": len(cands), "accepted": accepted, "rejected": rejected}
