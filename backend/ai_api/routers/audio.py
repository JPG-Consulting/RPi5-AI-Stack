from __future__ import annotations
from time import perf_counter
from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response

from ai_api.exceptions import ClientDisconnected
from ai_api.observability.metrics import metrics
from ai_api.tts_engine import PiperProcess, OggOpusEncoder
from ai_api.stt_engine import WhisperSTT
import lameenc

router = APIRouter()

class MP3Streamer:
    def __init__(self, sample_rate: int):
        self.encoder = lameenc.Encoder()
        self.encoder.set_bit_rate(64)
        self.encoder.set_in_sample_rate(sample_rate)
        self.encoder.set_channels(1)
        self.encoder.set_quality(2)

    def encode(self, pcm_bytes: bytes) -> bytes:
        return self.encoder.encode(pcm_bytes)

    def flush(self) -> bytes:
        try:
            return self.encoder.flush()
        except Exception:
            return b""

async def _disconnected(req: Request) -> bool:
    try:
        return await req.is_disconnected()  # type: ignore
    except TypeError:
        return False

@router.post("/v1/audio/speech")
async def tts(req: Request):
    t0 = perf_counter()
    app = req.app
    cfg = app.state.cfg
    body = await req.json()
    text = body.get("input", "")
    # OpenAI-compatible fields: input, model, voice, format
    _model = body.get("model")   # accepted but not used by Piper
    _voice = body.get("voice")   # accepted but not used by Piper
    # prefer 'format' (OpenAI); fallback to server default
    fmt = body.get("format", cfg.tts.default_format)

    metrics.inc("tts_requests_total")
    metrics.inc(f"tts_format_count_{fmt}")

    piper = PiperProcess(cfg.tts.piper.binary, cfg.tts.piper.model, cfg.tts.sample_rate)
    bytes_sent = 0
    cancelled = False

    if fmt == "opus":
        enc = OggOpusEncoder(cfg.tts.sample_rate)
        media_type = "audio/ogg"
    elif fmt == "mp3":
        enc = MP3Streamer(cfg.tts.sample_rate)
        media_type = "audio/mpeg"
    elif fmt == "pcm":
        enc = None
        media_type = "application/octet-stream"
    else:
        return JSONResponse({"error": f"Unsupported format: {fmt}"}, status_code=400)

    async def stream():
        nonlocal bytes_sent, cancelled
        try:
            piper.write(text)

            if fmt == "opus":
                for pcm in piper.read_pcm():
                    if await _disconnected(req):
                        raise ClientDisconnected()
                    enc.write(pcm)
                enc.close()
                for ogg in enc.read():
                    bytes_sent += len(ogg)
                    yield ogg
            else:
                for pcm in piper.read_pcm():
                    if await _disconnected(req):
                        raise ClientDisconnected()
                    if enc is None:
                        bytes_sent += len(pcm)
                        yield pcm
                    else:
                        out = enc.encode(pcm)
                        if out:
                            bytes_sent += len(out)
                            yield out

            metrics.inc("tts_success_total")
        except ClientDisconnected:
            cancelled = True
            metrics.inc("tts_cancelled_total")
        except Exception:
            metrics.inc("tts_error_total")
            raise
        finally:
            piper.terminate()
            if fmt == "opus":
                enc.terminate()
            elif fmt == "mp3":
                # ensure encoder emits final bytes
                try:
                    tail = enc.flush()
                    if tail:
                        bytes_sent += len(tail)
                        yield tail
                except Exception:
                    pass
            metrics.inc("tts_audio_bytes_streamed_total", bytes_sent)
            metrics.observe_ms("tts_duration_ms", (perf_counter() - t0) * 1000)

    # OpenAI-compatible response: return binary audio with Content-Type and Content-Length
    chunks: list[bytes] = []
    try:
        async for c in stream():
            chunks.append(c)
    except ClientDisconnected:
        return JSONResponse({"error": "client disconnected"}, status_code=499)

    content = b"".join(chunks)
    headers: dict[str, str] = {}
    headers["Content-Length"] = str(len(content))
    return Response(content=content, media_type=media_type, headers=headers)

@router.post("/v1/audio/transcriptions")
async def stt(
    request: Request,
    file: UploadFile = File(...),
    model: str = Form(default="whisper-1"),
    language: str | None = Form(default=None),
):
    t0 = perf_counter()
    metrics.inc("stt_requests_total")
    try:
        audio = await file.read()
        metrics.inc("stt_audio_bytes_total", len(audio))
        stt_engine: WhisperSTT = request.app.state.stt
        text = stt_engine.transcribe(audio_bytes=audio, language=language or request.app.state.cfg.stt.language)
        metrics.inc("stt_success_total")
        return JSONResponse({"text": text})
    except Exception:
        metrics.inc("stt_error_total")
        raise
    finally:
        metrics.observe_ms("stt_duration_ms", (perf_counter() - t0) * 1000)
