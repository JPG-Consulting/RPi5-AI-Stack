from __future__ import annotations
import subprocess, signal

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
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0
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
            try:
                self.proc.send_signal(signal.SIGTERM)
            except Exception:
                pass
