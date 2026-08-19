"""Authenticated HTTP boundary for conversational assistance."""

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.config.settings import Settings, get_settings
from app.conversation.manager import ConversationAccessError, ConversationManager
from app.conversation.schemas import ChatRequest, ChatResponse
from app.conversation.service import ConversationService
from app.nlu.llm_client import LLMClientError, create_llm_client
from app.session.store import development_identity_store


router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])
_conversation_manager = ConversationManager()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    x_development_user_id: str = Header(..., alias="X-Development-User-Id"),
    settings: Settings = Depends(get_settings),
) -> ChatResponse:
    """Use a development authentication header; role and ownership never come from JSON."""
    identity = development_identity_store.get(x_development_user_id)
    if identity is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown development identity.")
    try:
        service = ConversationService(create_llm_client(settings), _conversation_manager)
        return await service.handle_message(identity, request.conversation_id, request.message)
    except ConversationAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conversation is not available.") from exc
    except LLMClientError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
