def test_metrics(client):
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "counters" in res.json()
