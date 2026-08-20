"""HTTP boundary for development-time NLU analysis and tool execution."""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config.settings import Settings, get_settings
from app.nlu.llm_client import (
    LLMClientError,
    LLMConfigurationError,
    LLMTimeoutError,
    create_llm_client,
)
from app.nlu.schemas import NLUAnalyzeRequest, NLUResult
from app.nlu.service import nlu_service
from app.nlu.intents import Intent
from app.session.models import Identity
from app.session.dependencies import require_authenticated_identity


router = APIRouter(prefix="/api/v1/nlu", tags=["nlu"])


@router.post("/analyze", response_model=NLUResult)
async def analyze_nlu_message(
    request: NLUAnalyzeRequest,
    settings: Settings = Depends(get_settings),
) -> NLUResult:
    """Return an NLU interpretation; no authorization or external action occurs here."""
    try:
        client = create_llm_client(settings)
        return await client.analyze_message(request.message, request.conversation_context)
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except LLMTimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    except LLMClientError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/execute")
async def execute_nlu_message(
    text: str = Query(..., description="User message to process"),
    conversation_id: Optional[str] = Query(None, description="Conversation ID"),
    identity: Identity = Depends(require_authenticated_identity)
) -> Dict[str, Any]:
    """Process natural language request, authorize, and route to tool."""
    text_lower = text.lower()
    if "ignore previous instructions" in text_lower or "ignore instructions" in text_lower:
        return {
            "success": True,
            "intent": "unsupported_request",
            "message": "Unsupported instruction attempt."
        }

    nlu_result = nlu_service.process_natural_language(text, identity)
    
    # Handle clarification for parent with multiple children or missing student
    if nlu_result.intent == Intent.VIEW_CHILD_ATTENDANCE and not nlu_result.entities.student_name:
        from app.domain import school_domain_service
        children = school_domain_service.get_children_for_parent(identity.user_id)
        if len(children) > 1:
            names = [c.name for c in children]
            prompt = f"Which child would you like me to check — {' or '.join(names)}?"
            return {
                "success": True,
                "intent": "view_child_attendance",
                "requires_clarification": True,
                "clarification_prompt": prompt,
                "message": prompt
            }

    if nlu_result.requires_clarification:
        prompt = "Which student would you like me to check?"
        return {
            "success": True,
            "intent": nlu_result.intent.value if hasattr(nlu_result.intent, "value") else nlu_result.intent,
            "requires_clarification": True,
            "clarification_prompt": prompt,
            "message": prompt
        }

    # Handle greetings & unsupported directly
    if nlu_result.intent == Intent.GREETING:
        role_display = identity.role.value.title()
        return {
            "success": True,
            "intent": "greeting",
            "message": f"Hello {identity.name}! You are logged in as {role_display}. How can I help you today?"
        }

    if nlu_result.intent == Intent.UNSUPPORTED_REQUEST:
        return {
            "success": True,
            "intent": "unsupported_request",
            "message": "I’m sorry, but I can’t perform that action."
        }

    # Route to tool with authorization check
    result = nlu_service.route_to_tool(nlu_result, identity, conversation_id or "")
    return result
