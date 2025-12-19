def test_tts_pcm_stream(client):
    res = client.post(
        "/v1/audio/speech",
        json={"input": "Hola", "format": "pcm"},
    )
    assert res.status_code == 200
    content = res.content
    assert isinstance(content, (bytes, bytearray))
    assert len(content) > 0
