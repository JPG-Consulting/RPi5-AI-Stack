from __future__ import annotations
import os, shutil, subprocess, signal, logging

logger = logging.getLogger(__name__)

class PiperProcess:
    def __init__(self, binary: str, model: str, sample_rate: int):
        self.binary = self._resolve_binary(binary)
        self.proc = subprocess.Popen(
            [self.binary, "--model", model, "--output-raw", "--sample-rate", str(sample_rate)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
            env=self._build_env(),
        )

    def _resolve_binary(self, binary: str) -> str:
        """
        Prefer a headless Piper CLI. If the configured path is not found,
        try common CLI binary names before falling back.
        """
        candidates = []
        # exact path or PATH resolution for provided binary
        candidates.append(binary)
        resolved = shutil.which(binary)
        if resolved:
            candidates.append(resolved)
        # common CLI binary name installed by upstream builds
        alt = shutil.which("piper-tts")
        if alt:
            candidates.append(alt)
        for cand in candidates:
            if cand and os.path.exists(cand) and os.access(cand, os.X_OK):
                if cand != binary:
                    logger.info("Using Piper binary override: %s -> %s", binary, cand)
                return cand
        # fallback to original value; subprocess will raise a clearer error
        logger.warning("Piper binary not found; attempting to run configured path: %s", binary)
        return binary

    def _build_env(self) -> dict[str, str]:
        env = dict(os.environ)
        # Some Piper Python wrappers try to load Gtk; disable GUI usage if respected.
        env.setdefault("PIPER_NO_GUI", "1")
        return env

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
