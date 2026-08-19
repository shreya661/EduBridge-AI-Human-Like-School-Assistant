"""Deterministic ownership validation kept separate from role permissions."""

from app.authz.guard import AuthorizationReason, AuthorizationResult
from app.nlu.intents import Intent
from app.session.models import Identity


def validate_ownership(
    identity: Identity,
    intent: Intent,
    *,
    student_id: str | None = None,
    class_name: str | None = None,
) -> AuthorizationResult:
    """Check identity-to-target relationships after RBAC has permitted an intent."""
    if intent == Intent.VIEW_OWN_ATTENDANCE:
        if student_id is None:
            return _target_required()
        return _result(identity.student_id == student_id)

    if intent == Intent.VIEW_CHILD_ATTENDANCE:
        if student_id is None:
            return _target_required()
        return _result(student_id in identity.associated_student_ids)

    if intent in {Intent.VIEW_CLASS_ATTENDANCE, Intent.MARK_ATTENDANCE}:
        if class_name is None:
            return _target_required()
        return _result(class_name in identity.assigned_class_names)

    return AuthorizationResult(allowed=True, reason=AuthorizationReason.ALLOWED)


def _result(allowed: bool) -> AuthorizationResult:
    if allowed:
        return AuthorizationResult(allowed=True, reason=AuthorizationReason.ALLOWED)
    return AuthorizationResult(
        allowed=False,
        reason=AuthorizationReason.OWNERSHIP_CHECK_FAILED,
    )


def _target_required() -> AuthorizationResult:
    return AuthorizationResult(allowed=False, reason=AuthorizationReason.TARGET_REQUIRED)
