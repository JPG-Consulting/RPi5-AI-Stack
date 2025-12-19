import json

from ai_api.tts_engine import DEFAULT_SAMPLE_RATE, resolve_voice_config


def test_resolve_voice_config_uses_metadata_when_present(tmp_path):
    model_path = tmp_path / "voice.onnx"
    model_path.write_bytes(b"")
    metadata = {"audio": {"sample_rate": 16000}}
    config_path = model_path.with_suffix(".json")
    config_path.write_text(json.dumps(metadata), encoding="utf-8")

    voice_cfg = resolve_voice_config(str(model_path))

    assert voice_cfg.sample_rate == 16000
    assert voice_cfg.config_path == str(config_path)


def test_resolve_voice_config_fallback_without_metadata(tmp_path):
    model_path = tmp_path / "voice.onnx"
    model_path.write_bytes(b"")

    voice_cfg = resolve_voice_config(str(model_path))

    assert voice_cfg.sample_rate == DEFAULT_SAMPLE_RATE
    assert voice_cfg.config_path is None
