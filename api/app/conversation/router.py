"""Authenticated HTTP boundary for conversational assistance and conversation management."""

from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Header, Cookie, HTTPException, status

from app.config.settings import Settings, get_settings
from app.conversation.manager import ConversationAccessError, ConversationManager
from app.conversation.schemas import ChatRequest, ChatResponse
from app.conversation.service import ConversationService
from app.nlu.llm_client import LLMClientError, create_llm_client
from app.session.store import development_identity_store
from app.session.session_manager import session_store
from app.session.models import Identity
from app.session.dependencies import require_authenticated_identity


router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])
conversation_router = APIRouter(prefix="/api/v1/conversation", tags=["conversation"])

_conversation_manager = ConversationManager()


class ConversationModel(BaseModel):
    id: str
    user_id: str
    created_at: datetime = datetime.now()


async def resolve_chat_identity(
    x_development_user_id: Optional[str] = Header(None, alias="X-Development-User-Id"),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    session_id: Optional[str] = Cookie(None),
) -> Identity:
    """Resolve identity via session token or development header."""
    token = x_session_id or session_id
    if token:
        session_data = session_store.get_session(token)
        if session_data:
            return session_data.identity

    if x_development_user_id:
        identity = development_identity_store.get(x_development_user_id)
        if identity:
            return identity

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    identity: Identity = Depends(resolve_chat_identity),
    settings: Settings = Depends(get_settings),
) -> ChatResponse:
    """Session-backed conversational endpoint with deterministic authorization & tool routing."""
    try:
        service = ConversationService(create_llm_client(settings), _conversation_manager)
        return await service.handle_message(identity, request.conversation_id, request.message)
    except ConversationAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conversation is not available.") from exc
    except LLMClientError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@conversation_router.post("/", response_model=ConversationModel)
async def create_conversation(identity: Identity = Depends(require_authenticated_identity)) -> ConversationModel:
    """Create a new conversation for authenticated user."""
    context = _conversation_manager.get_or_create(None, identity)
    return ConversationModel(id=context.conversation_id, user_id=identity.user_id)


@conversation_router.get("/{conversation_id}", response_model=ConversationModel)
async def get_conversation(conversation_id: str, identity: Identity = Depends(require_authenticated_identity)) -> ConversationModel:
    """Get conversation details."""
    try:
        context = _conversation_manager.get_or_create(conversation_id, identity)
        return ConversationModel(id=context.conversation_id, user_id=identity.user_id)
    except ConversationAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied") from exc
