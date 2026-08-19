"""Development-only authorization check endpoint."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.authz.guard import AuthorizationResult, is_allowed
from app.authz.ownership import validate_ownership
from app.nlu.intents import Intent
from app.session.store import development_identity_store


class AuthorizationCheckRequest(BaseModel):
    """Authorization input without caller-controlled identity or role fields."""

    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1)
    intent: Intent
    target_student_id: str | None = None
    target_class_name: str | None = None


router = APIRouter(prefix="/api/v1/authz", tags=["authorization"])


@router.post("/check", response_model=AuthorizationResult)
async def check_authorization(request: AuthorizationCheckRequest) -> AuthorizationResult:
    """Evaluate RBAC and ownership using a development session identity lookup."""
    identity = development_identity_store.get(request.user_id)
    if identity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Development identity was not found.",
        )

    role_result = is_allowed(identity, request.intent)
    if not role_result.allowed:
        return role_result

    return validate_ownership(
        identity,
        request.intent,
        student_id=request.target_student_id,
        class_name=request.target_class_name,
    )
