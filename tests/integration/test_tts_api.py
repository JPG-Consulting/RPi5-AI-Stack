def test_tts_pcm_stream(client):
    res = client.post(
        "/v1/audio/speech",
        json={"input": "Hola", "response_format": "pcm"},
        stream=True
    )
    assert res.status_code == 200
    chunk = next(res.iter_bytes(), b"")
    assert isinstance(chunk, (bytes, bytearray))
