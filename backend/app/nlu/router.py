"""HTTP boundary for development-time NLU analysis."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.config.settings import Settings, get_settings
from app.nlu.llm_client import (
    LLMClientError,
    LLMConfigurationError,
    LLMTimeoutError,
    create_llm_client,
)
from app.nlu.schemas import NLUAnalyzeRequest, NLUResult


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
