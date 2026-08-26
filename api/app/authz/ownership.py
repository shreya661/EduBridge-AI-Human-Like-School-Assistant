# backend/app/authz/ownership.py
from typing import Optional, Union, Any
from app.session.models import Identity, Role
from app.domain import school_domain_service
from app.nlu.intents import Intent


def validate_student_ownership(identity: Identity, target_student_id: str) -> bool:
    """Validate if identity has ownership/permission to access target student using domain data"""
    if identity.role == Role.STUDENT:
        # Student can only access their own data - need to map identity.user_id to student_id
        # This requires checking if the authenticated user is linked to this student
        # Since we removed associated_student_ids from Identity, we need to check via domain
        # In the current setup, we need to know which student the authenticated user represents
        # For students, we assume user_id matches student_id for simplicity in this MVP
        return identity.user_id == target_student_id or identity.student_id == target_student_id
    
    elif identity.role == Role.PARENT:
        # Parent can access associated students via domain relationship
        children = school_domain_service.get_children_for_parent(identity.user_id)
        return target_student_id in [child.student_id for child in children]
    
    elif identity.role == Role.TEACHER:
        # Teacher can access students in their assigned classes
        classes = school_domain_service.get_classes_for_teacher(identity.user_id)
        for class_ in classes:
            students = school_domain_service.get_students_in_class(class_.class_id)
            if target_student_id in [s.student_id for s in students]:
                return True
        return False
    
    elif identity.role == Role.PRINCIPAL:
        # Principal can access any student
        return True
    
    return False


def validate_ownership(
    identity: Identity,
    arg: Union[Intent, str] = Intent.UNKNOWN,
    *,
    student_id: Optional[str] = None,
    class_name: Optional[str] = None,
) -> Union[Any, bool]:
    """Validate if identity has ownership/permission to access target student using domain data"""
    # Direct student ID string check
    if isinstance(arg, str) and not isinstance(arg, Intent) and student_id is None and class_name is None:
        return validate_student_ownership(identity, arg)

    from app.authz.guard import AuthorizationReason, AuthorizationResult

    intent = arg if isinstance(arg, Intent) else Intent.UNKNOWN

    if intent == Intent.VIEW_OWN_ATTENDANCE:
        if student_id is None:
            return AuthorizationResult(allowed=False, reason=AuthorizationReason.TARGET_REQUIRED)
        allowed = (identity.student_id == student_id or identity.user_id == student_id)
        return AuthorizationResult(
            allowed=allowed,
            reason=AuthorizationReason.ALLOWED if allowed else AuthorizationReason.OWNERSHIP_CHECK_FAILED,
        )

    if intent == Intent.VIEW_CHILD_ATTENDANCE:
        if student_id is None:
            return AuthorizationResult(allowed=False, reason=AuthorizationReason.TARGET_REQUIRED)
        allowed = validate_student_ownership(identity, student_id)
        return AuthorizationResult(
            allowed=allowed,
            reason=AuthorizationReason.ALLOWED if allowed else AuthorizationReason.OWNERSHIP_CHECK_FAILED,
        )

    if intent in {Intent.VIEW_CLASS_ATTENDANCE, Intent.MARK_ATTENDANCE}:
        if class_name is None:
            return AuthorizationResult(allowed=False, reason=AuthorizationReason.TARGET_REQUIRED)
        classes = school_domain_service.get_classes_for_teacher(identity.user_id)
        assigned = [c.class_id for c in classes] + [c.name for c in classes]
        if hasattr(identity, "assigned_class_names") and identity.assigned_class_names:
            assigned.extend(identity.assigned_class_names)
        allowed = class_name in assigned or identity.role == Role.PRINCIPAL
        return AuthorizationResult(
            allowed=allowed,
            reason=AuthorizationReason.ALLOWED if allowed else AuthorizationReason.OWNERSHIP_CHECK_FAILED,
        )

    return AuthorizationResult(allowed=True, reason=AuthorizationReason.ALLOWED)
