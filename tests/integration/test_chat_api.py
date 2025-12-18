def test_chat_basic(client):
    res = client.post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "Hola"}], "stream": False}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["choices"][0]["message"]["role"] == "assistant"
