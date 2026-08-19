"""Deterministic RBAC checks independent of messages and LLM output."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from app.authz.rbac_table import ROLE_PERMISSIONS
from app.nlu.intents import Intent
from app.nlu.schemas import NLUResult
from app.session.models import Identity


class AuthorizationReason(StrEnum):
    ALLOWED = "allowed"
    ROLE_NOT_PERMITTED = "role_not_permitted"
    OWNERSHIP_CHECK_FAILED = "ownership_check_failed"
    TARGET_REQUIRED = "target_required"


class AuthorizationResult(BaseModel):
    """Explicit outcome returned by deterministic authorization checks."""

    model_config = ConfigDict(frozen=True)

    allowed: bool
    reason: AuthorizationReason


def is_allowed(identity: Identity, intent: Intent) -> AuthorizationResult:
    """Check role permissions using only trusted application identity data."""
    if intent in ROLE_PERMISSIONS[identity.role]:
        return AuthorizationResult(allowed=True, reason=AuthorizationReason.ALLOWED)
    return AuthorizationResult(
        allowed=False,
        reason=AuthorizationReason.ROLE_NOT_PERMITTED,
    )


def authorize_nlu_result(identity: Identity, nlu_result: NLUResult) -> AuthorizationResult:
    """Authorize only the controlled intent from NLU using trusted session identity."""
    return is_allowed(identity, nlu_result.intent)
