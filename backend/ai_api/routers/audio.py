from __future__ import annotations

from fastapi import APIRouter, Request, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, Response, JSONResponse

from ai_api.config import get_config
from ai_api.tts_engine import PiperProcess
from ai_api.stt.whisper_engine import WhisperEngine

router = APIRouter()

# =========================================================
# Text-to-Speech (OpenAI-compatible)
# POST /v1/audio/speech
# =========================================================

@router.post("/v1/audio/speech")
async def tts(req: Request):
    body = await req.json()

    text = body.get("input")
    if not text:
        raise HTTPException(status_code=400, detail="Missing input text")

    response_format = body.get("response_format", "mp3")
    stream = body.get("stream", False)

    cfg = get_config()

    if cfg.tts.engine != "piper":
        raise HTTPException(status_code=400, detail="TTS engine not enabled")

    piper = PiperProcess(
        cfg.tts.piper.binary,
        cfg.tts.piper.model,
        cfg.tts.sample_rate,
    )

    # -------------------------------------------------
    # NON-STREAMING MODE (browser-safe, OpenAI-like)
    # -------------------------------------------------
    if not stream:
        try:
            audio_bytes = piper.synthesize_bytes(
                text,
                output_format=response_format,
            )
        finally:
            piper.close()

        media_type = {
            "mp3": "audio/mpeg",
            "opus": "audio/ogg",
            "wav": "audio/wav",
            "pcm": "application/octet-stream",
        }.get(response_format, "application/octet-stream")

        return Response(
            content=audio_bytes,
            media_type=media_type,
            headers={
                "X-Audio-Format": response_format,
                "X-Audio-Sample-Rate": str(cfg.tts.sample_rate),
            },
        )

    # -------------------------------------------------
    # STREAMING MODE (advanced clients / embedded)
    # -------------------------------------------------
    async def audio_stream():
        try:
            async for chunk in piper.synthesize_stream(
                text,
                output_format=response_format,
            ):
                if await req.is_disconnected():
                    break
                yield chunk
        finally:
            piper.close()

    media_type = {
        "mp3": "audio/mpeg",
        "opus": "audio/ogg",
        "pcm": "application/octet-stream",
    }.get(response_format, "application/octet-stream")

    return StreamingResponse(
        audio_stream(),
        media_type=media_type,
        headers={
            "X-Audio-Format": response_format,
            "X-Audio-Sample-Rate": str(cfg.tts.sample_rate),
        },
    )


# =========================================================
# Speech-to-Text (OpenAI-compatible)
# POST /v1/audio/transcriptions
# =========================================================

@router.post("/v1/audio/transcriptions")
async def transcriptions(
    file: UploadFile = File(...),
    model: str | None = None,
    language: str | None = None,
):
    cfg = get_config()

    if cfg.stt.engine != "whisper":
        raise HTTPException(status_code=400, detail="STT engine not enabled")

    whisper = WhisperEngine(
        model=cfg.stt.whisper.model,
        language=language or cfg.stt.language,
        device=cfg.stt.device,
        compute_type=cfg.stt.compute_type,
    )

    try:
        audio_bytes = await file.read()
        text = whisper.transcribe_bytes(audio_bytes)
    finally:
        await file.close()

    # OpenAI-compatible response
    return JSONResponse({
        "text": text
    })
