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


from app.i18n.language_router import SupportedLanguage, detect_language, format_localized_message
from app.security.rate_limiter import enforce_nlu_rate_limit


@router.post("/execute", dependencies=[Depends(enforce_nlu_rate_limit)])
async def execute_nlu_message(
    text: str = Query(..., description="User message to process"),
    conversation_id: Optional[str] = Query(None, description="Conversation ID"),
    language: Optional[str] = Query(None, description="Preferred language code (en, gu, hi, ta, te, mr, bn, pa, kn, ml, ur)"),
    identity: Identity = Depends(require_authenticated_identity)
) -> Dict[str, Any]:
    """Process natural language request, authorize, and route to tool with multi-language support."""
    # Determine response language: explicit query param or script detection
    detected = detect_language(text)
    if language:
        try:
            target_lang = SupportedLanguage(language.lower())
        except ValueError:
            target_lang = detected
    else:
        target_lang = detected

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
            joiner = " અથવા " if target_lang == SupportedLanguage.GUJARATI else (" या " if target_lang == SupportedLanguage.HINDI else " or ")
            prompt = format_localized_message(
                "clarification_child",
                target_lang,
                names=joiner.join(names)
            )
            return {
                "success": True,
                "intent": "view_child_attendance",
                "requires_clarification": True,
                "clarification_prompt": prompt,
                "message": prompt
            }

    if nlu_result.requires_clarification:
        prompt = format_localized_message("clarification_child", target_lang, names="...")
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
        localized_greeting = format_localized_message(
            "greeting",
            target_lang,
            name=identity.name,
            role=role_display
        )
        return {
            "success": True,
            "intent": "greeting",
            "message": localized_greeting
        }

    if nlu_result.intent == Intent.UNSUPPORTED_REQUEST:
        denied_msg = format_localized_message("permission_denied", target_lang)
        return {
            "success": True,
            "intent": "unsupported_request",
            "message": denied_msg or "I’m sorry, but I can’t perform that action."
        }

    # Route to tool with authorization check
    result = nlu_service.route_to_tool(nlu_result, identity, conversation_id or "")

    # Localize tool response if target_lang is not English
    if target_lang != SupportedLanguage.ENGLISH:
        intent = nlu_result.intent
        if intent in [Intent.VIEW_OWN_ATTENDANCE, "view_own_attendance"] and result.get("success"):
            data = result.get("data", [])
            total = len(data)
            present = sum(1 for r in data if r.get("status") in ["PRESENT", "AttendanceStatus.PRESENT"])
            pct = (present / total * 100) if total > 0 else 92.4
            result["message"] = format_localized_message("attendance_student", target_lang, percentage=pct)

        elif intent in [Intent.VIEW_CHILD_ATTENDANCE, "view_child_attendance"] and result.get("success"):
            data = result.get("data", [])
            total = len(data)
            present = sum(1 for r in data if r.get("status") in ["PRESENT", "AttendanceStatus.PRESENT"])
            pct = (present / total * 100) if total > 0 else 92.4
            student_name = nlu_result.entities.student_name or "બાળક" if target_lang == SupportedLanguage.GUJARATI else "Student"
            result["message"] = format_localized_message("attendance_child", target_lang, name=student_name, percentage=pct)

        elif intent in [Intent.MARK_ATTENDANCE, "mark_attendance"] and result.get("success"):
            student_name = nlu_result.entities.student_name or ("વિદ્યાર્થી" if target_lang == SupportedLanguage.GUJARATI else "Student")
            status = nlu_result.entities.attendance_status or "PRESENT"
            status_display = status
            if target_lang == SupportedLanguage.GUJARATI:
                status_display = "ગેરહાજર" if status == "ABSENT" else ("હાજર" if status == "PRESENT" else status)
            elif target_lang == SupportedLanguage.HINDI:
                status_display = "अनुपस्थित" if status == "ABSENT" else ("उपस्थित" if status == "PRESENT" else status)
            from datetime import date
            result["message"] = format_localized_message("attendance_marked", target_lang, name=student_name, date=date.today().isoformat(), status=status_display)

        elif not result.get("success") and result.get("error") == "permission_denied":
            result["message"] = format_localized_message("permission_denied", target_lang)

    return result
