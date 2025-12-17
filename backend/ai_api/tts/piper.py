from __future__ import annotations
import subprocess, signal

class PiperProcess:
    def __init__(self, binary: str, model: str, sample_rate: int):
        self.proc = subprocess.Popen(
            [binary, "--model", model, "--output-raw", "--sample-rate", str(sample_rate)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0
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
            try:
                self.proc.send_signal(signal.SIGTERM)
            except Exception:
                pass
