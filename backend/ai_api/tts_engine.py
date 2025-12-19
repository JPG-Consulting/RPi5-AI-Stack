from __future__ import annotations

import json
import logging
import signal
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
    """

    meta_path = Path(model_path).with_suffix(".json")
    metadata: dict[str, Any] | None = None

    if meta_path.exists():
        try:
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            logger.warning("Failed to parse Piper metadata at %s; continuing without it", meta_path)

    sample_rate = _extract_sample_rate(metadata) if metadata else None
    config_path = str(meta_path) if metadata is not None else None

    if sample_rate:
        return VoiceConfig(config_path=config_path, sample_rate=sample_rate)

    return VoiceConfig(config_path=config_path, sample_rate=fallback_sample_rate)


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
        self.proc.stdin.write(text.encode("utf-8"))
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
