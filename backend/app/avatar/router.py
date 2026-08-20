"""Avatar API Router: Streaming Session Creation & Lip-Sync Rendering."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.session.models import Identity
from app.session.dependencies import require_authenticated_identity
from app.avatar.provider import avatar_provider, AvatarSession, AvatarRenderResult
from app.i18n.language_router import SupportedLanguage, detect_language


router = APIRouter(prefix="/api/v1/avatar", tags=["avatar"])


class AvatarSessionRequest(BaseModel):
    avatar_id: Optional[str] = "school_assistant_v1"


class AvatarSpeakRequest(BaseModel):
    session_id: str
    text: str
    language: Optional[str] = "en"


@router.post("/session", response_model=Dict[str, Any])
async def create_avatar_session_endpoint(
    payload: AvatarSessionRequest,
    identity: Identity = Depends(require_authenticated_identity)
) -> Dict[str, Any]:
    """Start an interactive WebRTC avatar session."""
    session: AvatarSession = avatar_provider.create_session(
        user_id=identity.user_id,
        avatar_id=payload.avatar_id
    )
    return {
        "session_id": session.session_id,
        "avatar_id": session.avatar_id,
        "status": session.status,
        "ice_servers": session.ice_servers,
        "created_at": session.created_at
    }


@router.post("/speak", response_model=Dict[str, Any])
async def avatar_speak_endpoint(
    payload: AvatarSpeakRequest,
    identity: Identity = Depends(require_authenticated_identity)
) -> Dict[str, Any]:
    """Render avatar speech with synchronous lip-sync viseme cues."""
    if not payload.text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Text cannot be empty.")

    try:
        lang_enum = SupportedLanguage(payload.language) if payload.language else detect_language(payload.text)
    except ValueError:
        lang_enum = SupportedLanguage.ENGLISH

    render_res: AvatarRenderResult = avatar_provider.render_speech(
        session_id=payload.session_id,
        text=payload.text,
        language=lang_enum
    )

    return {
        "session_id": render_res.session_id,
        "text": render_res.text,
        "audio_base64": render_res.audio_base64,
        "viseme_cues": [v.dict() if hasattr(v, "dict") else v.model_dump() for v in render_res.viseme_cues],
        "video_stream_url": render_res.video_stream_url,
        "duration_seconds": render_res.duration_seconds
    }
