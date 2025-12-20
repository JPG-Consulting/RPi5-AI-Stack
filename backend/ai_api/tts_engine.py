from __future__ import annotations

import json
import logging
import signal
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import unicodedata

logger = logging.getLogger(__name__)

DEFAULT_SAMPLE_RATE = 22050


@dataclass
class VoiceConfig:
    config_path: str | None
    sample_rate: int


def _extract_sample_rate(metadata: dict[str, Any]) -> int | None:
    """Try to find a positive sample rate in common Piper metadata shapes."""

    def _get(path: tuple[str, ...]) -> Any:
        cur: Any = metadata
        for key in path:
            if isinstance(cur, dict) and key in cur:
                cur = cur[key]
            else:
                return None
        return cur

    for key_path in (
        ("audio", "sample_rate"),
        ("audio", "sampleRate"),
        ("sample_rate",),
        ("sampleRate",),
    ):
        val = _get(key_path)
        if isinstance(val, (int, float)) and int(val) > 0:
            return int(val)
    return None


def resolve_voice_config(model_path: str, fallback_sample_rate: int = DEFAULT_SAMPLE_RATE) -> VoiceConfig:
    """Resolve Piper config path (if JSON exists) and effective sample rate for encoders.

    Falls back to `fallback_sample_rate` when metadata is missing or lacks a sample rate.
    Tries both `<model>.json` and `<model>.onnx.json` because Piper models are commonly
    distributed with the latter naming scheme.
    """

    model = Path(model_path)
    candidate_meta_paths = [model.with_suffix(".json"), Path(f"{model_path}.json")]

    metadata: dict[str, Any] | None = None
    used_meta_path: Path | None = None

    for meta_path in candidate_meta_paths:
        if not meta_path.exists():
            continue
        try:
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            used_meta_path = meta_path
            break
        except Exception:
            logger.warning("Failed to parse Piper metadata at %s; continuing without it", meta_path)

    sample_rate = _extract_sample_rate(metadata) if metadata else None
    config_path = str(used_meta_path) if metadata is not None and used_meta_path else None

    if sample_rate:
        return VoiceConfig(config_path=config_path, sample_rate=sample_rate)

    return VoiceConfig(config_path=config_path, sample_rate=fallback_sample_rate)


def sanitize_tts_text(text: str) -> str:
    """Normalize and strip characters Piper cannot pronounce reliably.

    Removes control/zero-width characters, collapses whitespace, and trims the
    result so we do not feed garbage tokens that sound like noise.
    """

    normalized = unicodedata.normalize("NFKC", text)
    cleaned_chars: list[str] = []

    for ch in normalized:
        if ch in {"\n", "\r", "\t"}:
            cleaned_chars.append(" ")
            continue

        if unicodedata.category(ch).startswith("C"):
            # Drop control characters and zero-width marks that surface as noise
            # in Piper output.
            continue

        cleaned_chars.append(ch)

    cleaned = "".join(cleaned_chars)
    collapsed = " ".join(cleaned.split())
    return collapsed.strip()


class PiperProcess:
    def __init__(self, binary: str, model: str, sample_rate: int, config_path: str | None):
        cmd = [binary, "--model", model, "--output-raw"]
        if config_path:
            cmd.extend(["-c", config_path])

        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
        )

    def write(self, text: str):
        assert self.proc.stdin
        payload = text if text.endswith("\n") else f"{text}\n"
        self.proc.stdin.write(payload.encode("utf-8"))
        self.proc.stdin.close()

    def read_pcm(self, chunk_size: int = 4096):
        assert self.proc.stdout
        while True:
            data = self.proc.stdout.read(chunk_size)
            if not data:
                break
            yield data

    def terminate(self):
        if self.proc.poll() is None:
            self.proc.send_signal(signal.SIGTERM)


class OggOpusEncoder:
    def __init__(self, sample_rate: int):
        self.proc = subprocess.Popen(
            [
                "ffmpeg",
                "-f",
                "s16le",
                "-ar",
                str(sample_rate),
                "-ac",
                "1",
                "-i",
                "pipe:0",
                "-c:a",
                "libopus",
                "-application",
                "voip",
                "-f",
                "ogg",
                "pipe:1",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
        )

    def write(self, pcm: bytes):
        assert self.proc.stdin
        self.proc.stdin.write(pcm)

    def close(self):
        if self.proc.stdin:
            self.proc.stdin.close()

    def read(self, chunk_size: int = 4096):
        assert self.proc.stdout
        while True:
            data = self.proc.stdout.read(chunk_size)
            if not data:
                break
            yield data

    def terminate(self):
        if self.proc.poll() is None:
            self.proc.send_signal(signal.SIGTERM)
