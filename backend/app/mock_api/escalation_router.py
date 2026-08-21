"""HTTP Router for Escalation / Support tickets."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.session.models import Identity
from app.session.dependencies import require_authenticated_identity
from app.authz.guard import authorize_request_detailed 
from app.tools.escalation_tool import escalation_tool
from app.mock_api.escalation import escalation_service, EscalationTicket


router = APIRouter(prefix="/api/v1/escalate", tags=["escalation"])


class EscalationCreateRequest(BaseModel):
    target: str = "teacher"  # "teacher" or "management"
    reason: Optional[str] = "General query / Human intervention requested"
    student_id: Optional[str] = None


@router.post("", response_model=Dict[str, Any])
async def create_escalation_endpoint(
    payload: EscalationCreateRequest,
    identity: Identity = Depends(require_authenticated_identity)
) -> Dict[str, Any]:
    """Create human escalation ticket after verifying authorization."""
    target_clean = "teacher" if "teacher" in payload.target.lower() else "management"
    intent_check = f"escalate_to_{target_clean}"

    # Enforce escalation throttling (max 3 tickets / 10 mins)
    from app.security.rate_limiter import escalation_limiter
    allowed, retry_after = escalation_limiter.check_and_record(identity.user_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Escalation ticket limit reached (max 3 per 10 minutes). Please try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)}
        )

    auth_result = authorize_request_detailed(identity, intent_check)
    if not auth_result.allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this escalation."
        )

    res = escalation_tool.execute(
        identity=identity,
        target=target_clean,
        reason=payload.reason,
        student_id=payload.student_id
    )
    return res


@router.get("/tickets", response_model=Dict[str, Any])
async def list_my_tickets(
    identity: Identity = Depends(require_authenticated_identity)
) -> Dict[str, Any]:
    """List escalation tickets submitted by current authenticated user."""
    tickets = escalation_service.list_tickets_for_user(identity.user_id)
    return {
        "user_id": identity.user_id,
        "count": len(tickets),
        "tickets": [t.dict() if hasattr(t, "dict") else t.model_dump() for t in tickets]
    }
