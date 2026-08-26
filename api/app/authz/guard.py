# backend/app/authz/guard.py
from enum import StrEnum
from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

from app.session.models import Identity, Role
from app.authz.rbac_table import ROLE_PERMISSIONS, has_permission
from app.nlu.intents import Intent
from app.nlu.schemas import NLUResult


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


def authorize_request(identity: Identity, intent: str, target_data: Optional[Dict[str, Any]] = None) -> bool:
    """Authorize request based on identity and intent"""
    from app.authz.ownership import validate_ownership

    # Convert intent to permission (simplified mapping)
    permission_map = {
        "view_student_profile": "view_child_profile" if identity.role == Role.PARENT else "view_student_profiles",
        "view_student_grades": "view_child_grades" if identity.role == Role.PARENT else "view_student_grades",
        "view_student_attendance": "view_child_attendance" if identity.role == Role.PARENT else "view_student_attendance",
        "view_own_profile": "view_own_profile",
        "view_own_grades": "view_own_grades",
        "view_own_attendance": "view_own_attendance",
        "view_class_roster": "view_class_roster",
        "view_all_students": "view_all_students",
        "manage_users": "manage_users",
        "generate_reports": "generate_reports"
    }
    
    permission = permission_map.get(intent)
    if not permission:
        return False
    
    # Check RBAC permission
    if not has_permission(identity.role, permission):
        return False
    
    # Check ownership if needed
    if target_data and "target_student_id" in target_data:
        target_student_id = target_data["target_student_id"]
        return bool(validate_ownership(identity, target_student_id))
    
    return True


def authorize_request_detailed(identity: Identity, intent: str, target_data: Optional[Dict[str, Any]] = None):
    """Authorize request and return full structured AuthorizationResult"""
    from app.authz.engine import AuthorizationEngine
    engine = AuthorizationEngine()
    return engine.authorize_request(identity, intent, target_data)

