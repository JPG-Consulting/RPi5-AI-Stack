from __future__ import annotations
import subprocess, signal

class PiperProcess:
    def __init__(self, binary: str, model: str, sample_rate: int):
        self.proc = subprocess.Popen(
            [binary, "--model", model, "--output-raw", "--sample-rate", str(sample_rate)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )

    def write(self, text: str):
        assert self.proc.stdin
        payload = text if text.endswith("\n") else f"{text}\n"
        self.proc.stdin.write(payload.encode("utf-8"))
        try:
            self.proc.stdin.flush()
        finally:
            self.proc.stdin.close()

    def read_pcm(self, chunk_size: int = 4096):
        assert self.proc.stdout
        while True:
            data = self.proc.stdout.read(chunk_size)
            if not data:
                break
            yield data

    def read_error(self) -> str:
        if self.proc.stderr:
            try:
                return self.proc.stderr.read().decode("utf-8", errors="ignore").strip()
            except Exception:
                return ""
        return ""

    def wait(self, timeout: float | None = None) -> int | None:
        try:
            return self.proc.wait(timeout=timeout)
        except Exception:
            return self.proc.returncode

    def terminate(self):
        if self.proc.poll() is None:
            self.proc.send_signal(signal.SIGTERM)
        try:
            self.proc.wait(timeout=0.2)
        except Exception:
            pass

class OggOpusEncoder:
    def __init__(self, sample_rate: int):
        self.proc = subprocess.Popen(
            [
                "ffmpeg",
                "-f", "s16le",
                "-ar", str(sample_rate),
                "-ac", "1",
                "-i", "pipe:0",
                "-c:a", "libopus",
                "-application", "voip",
                "-f", "ogg",
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
