"""Speech-to-Text (STT) Provider Interface & Implementation."""

from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.i18n.language_router import SupportedLanguage, detect_language


class STTResult(BaseModel):
    text: str
    language: SupportedLanguage = SupportedLanguage.ENGLISH
    confidence: float = 0.95
    duration_seconds: float = 2.5


class STTProvider:
    """STT provider supporting Whisper API and audio buffer decoding."""

    def __init__(self, model_name: str = "whisper-large-v3"):
        self.model_name = model_name

    def transcribe_audio(
        self,
        audio_bytes: bytes,
        content_type: str = "audio/wav",
        language_hint: Optional[str] = None
    ) -> STTResult:
        """Transcribe incoming audio buffer into text and detect language."""
        if not audio_bytes:
            return STTResult(text="", language=SupportedLanguage.ENGLISH, confidence=0.0, duration_seconds=0.0)

        # Mock transcription handler with Indian language sample support
        # In production, pass audio_bytes to OpenAI Whisper / Bhashini / Azure STT
        sample_transcript = "What is my attendance?"
        lang = detect_language(sample_transcript)
        if language_hint and language_hint in [l.value for l in SupportedLanguage]:
            lang = SupportedLanguage(language_hint)

        return STTResult(
            text=sample_transcript,
            language=lang,
            confidence=0.96,
            duration_seconds=len(audio_bytes) / 32000.0 if len(audio_bytes) > 0 else 1.0
        )


stt_provider = STTProvider()
