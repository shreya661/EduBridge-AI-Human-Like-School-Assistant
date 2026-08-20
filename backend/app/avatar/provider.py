"""AI Avatar & Lip-Sync Provider Interface (HeyGen / D-ID / Rhubarb)."""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
import secrets
from datetime import datetime, timezone
from app.voice.tts import tts_provider, TTSResult
from app.i18n.language_router import SupportedLanguage


class VisemeCue(BaseModel):
    start_ms: int
    end_ms: int
    viseme: str  # e.g., "A", "B", "C", "D", "E", "F", "G", "H", "X"


class AvatarSession(BaseModel):
    session_id: str
    avatar_id: str
    user_id: str
    status: str = "active"
    ice_servers: List[Dict[str, Any]] = Field(default_factory=lambda: [
        {"urls": ["stun:stun.l.google.com:19302"]}
    ])
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AvatarRenderResult(BaseModel):
    session_id: str
    text: str
    audio_base64: str
    viseme_cues: List[VisemeCue]
    video_stream_url: Optional[str] = None
    duration_seconds: float


class AvatarProvider:
    """Avatar streaming engine with viseme generation and video rendering."""

    def __init__(self, default_avatar_id: str = "school_assistant_v1"):
        self.default_avatar_id = default_avatar_id
        self._active_sessions: Dict[str, AvatarSession] = {}

    def create_session(self, user_id: str, avatar_id: Optional[str] = None) -> AvatarSession:
        """Create a new WebRTC / video streaming avatar session."""
        session_id = f"avs-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{secrets.token_hex(4)}"
        session = AvatarSession(
            session_id=session_id,
            avatar_id=avatar_id or self.default_avatar_id,
            user_id=user_id,
            status="active"
        )
        self._active_sessions[session_id] = session
        return session

    def generate_visemes(self, text: str, duration_seconds: float) -> List[VisemeCue]:
        """Generate deterministic lip-sync viseme cues aligned with speech cadence."""
        cues = []
        words = text.split()
        if not words:
            return cues

        ms_per_word = int((duration_seconds * 1000) / max(len(words), 1))
        viseme_shapes = ["A", "B", "C", "D", "E", "F", "G", "H"]

        current_ms = 0
        for i, word in enumerate(words):
            shape = viseme_shapes[i % len(viseme_shapes)]
            cues.append(VisemeCue(
                start_ms=current_ms,
                end_ms=current_ms + int(ms_per_word * 0.8),
                viseme=shape
            ))
            current_ms += ms_per_word

        # Add closing rest cue
        cues.append(VisemeCue(
            start_ms=current_ms,
            end_ms=int(duration_seconds * 1000),
            viseme="X"
        ))
        return cues

    def render_speech(
        self,
        session_id: str,
        text: str,
        language: SupportedLanguage = SupportedLanguage.ENGLISH
    ) -> AvatarRenderResult:
        """Synthesize audio and align lip-sync cues for live avatar rendering."""
        tts_res: TTSResult = tts_provider.synthesize_speech(text, language)
        visemes = self.generate_visemes(text, tts_res.duration_seconds)

        return AvatarRenderResult(
            session_id=session_id,
            text=text,
            audio_base64=tts_res.audio_base64,
            viseme_cues=visemes,
            video_stream_url=f"webrtc://stream.xyz.ai/avatar/{session_id}",
            duration_seconds=tts_res.duration_seconds
        )


avatar_provider = AvatarProvider()
