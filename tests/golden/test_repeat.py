import json

def test_repeat_fixture():
    data = json.load(open("tests/golden/repeat_does_not_pollute.json"))
    assert data["expect"]["repeat"] is True
    assert data["expect"]["context_growth"] == 0
