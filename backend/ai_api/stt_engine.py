from __future__ import annotations
from faster_whisper import WhisperModel
import tempfile, os

class WhisperSTT:
    def __init__(self, model: str, device: str, compute_type: str):
        self.model = WhisperModel(model, device=device, compute_type=compute_type)

    def transcribe(self, audio_bytes: bytes, language: str) -> str:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp = f.name
        try:
            segments, _info = self.model.transcribe(tmp, language=language, vad_filter=True)
            return "".join(seg.text for seg in segments).strip()
        finally:
            try: os.unlink(tmp)
            except OSError: pass
