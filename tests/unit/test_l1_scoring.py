from ai_api.facts.types import FactCandidate
from ai_api.facts.l1_rules import score_l1

def test_static_name_high_confidence():
    f = FactCandidate("user:default", "name", "Juan", "static", "Me llamo Juan")
    assert score_l1(f) >= 0.9

def test_dynamic_fact_zero():
    f = FactCandidate("user:default", "weather", "lluvia", "dynamic", "Hoy llueve")
    assert score_l1(f) == 0.0
