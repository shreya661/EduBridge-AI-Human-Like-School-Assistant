"""Voice API Router: STT Transcription & TTS Speech Synthesis."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.session.models import Identity
from app.session.dependencies import require_authenticated_identity
from app.voice.stt import stt_provider, STTResult
from app.voice.tts import tts_provider, TTSResult
from app.i18n.language_router import SupportedLanguage, detect_language


router = APIRouter(prefix="/api/v1/voice", tags=["voice"])


class SynthesisRequest(BaseModel):
    text: str
    language: Optional[str] = "en"
    speaker_gender: Optional[str] = "female"


@router.post("/transcribe", response_model=Dict[str, Any])
async def transcribe_audio_endpoint(
    file: UploadFile = File(...),
    language_hint: Optional[str] = Form(None),
    identity: Identity = Depends(require_authenticated_identity)
) -> Dict[str, Any]:
    """Transcribe uploaded audio file into structured text with language detection."""
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty audio file provided.")

    stt_res: STTResult = stt_provider.transcribe_audio(
        audio_bytes=content,
        content_type=file.content_type or "audio/wav",
        language_hint=language_hint
    )
    return {
        "text": stt_res.text,
        "language": stt_res.language.value,
        "confidence": stt_res.confidence,
        "duration_seconds": stt_res.duration_seconds
    }


@router.post("/synthesize", response_model=Dict[str, Any])
async def synthesize_speech_endpoint(
    payload: SynthesisRequest,
    identity: Identity = Depends(require_authenticated_identity)
) -> Dict[str, Any]:
    """Synthesize text into speech audio response."""
    if not payload.text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Text cannot be empty.")

    try:
        lang_enum = SupportedLanguage(payload.language) if payload.language else detect_language(payload.text)
    except ValueError:
        lang_enum = SupportedLanguage.ENGLISH

    tts_res: TTSResult = tts_provider.synthesize_speech(
        text=payload.text,
        language=lang_enum,
        speaker_gender=payload.speaker_gender or "female"
    )

    return {
        "audio_base64": tts_res.audio_base64,
        "content_type": tts_res.content_type,
        "language": tts_res.language.value,
        "sample_rate": tts_res.sample_rate,
        "duration_seconds": tts_res.duration_seconds
    }
